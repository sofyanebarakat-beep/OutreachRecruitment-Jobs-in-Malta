import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
const cors = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers":
      "authorization, x-client-info, apikey, content-type",
  },
  url = Deno.env.get("SUPABASE_URL")!,
  anon = Deno.env.get("SUPABASE_ANON_KEY")!,
  serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!,
  service = createClient(url, serviceKey);
Deno.serve(async (req) => {
  if (req.method === "OPTIONS") return new Response("ok", { headers: cors });
  try {
    const auth = req.headers.get("Authorization") || "",
      token = auth.replace(/^Bearer\s+/i, "");
    if (token !== serviceKey) {
      const client = createClient(url, anon, {
        global: { headers: { Authorization: auth } },
      });
      const { data } = await client.rpc("is_admin");
      if (!data) return json({ error: "Administrator access required" }, 403);
    }
    const input = await req.json();
    return ["scheduled_drafts", "campaign_drafts"].includes(input.action)
      ? await scheduled(
          Math.max(1, Math.min(Number(input.count) || 2, 5)),
          input.action === "campaign_drafts" ? input.campaign_id : undefined,
        )
      : json(await generate(input));
  } catch (e) {
    return json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      500,
    );
  }
});
async function scheduled(count: number, campaignId?: string) {
  const { data: settings } = await service
    .from("seo_automation_settings")
    .select("*")
    .eq("id", "autopilot")
    .maybeSingle();
  if (settings && !settings.enabled)
    return json({ created: [], message: "Autopilot paused" });
  const limit = settings?.drafts_per_run || count,
    log = await service
      .from("seo_automation_logs")
      .insert({
        job_name: "SEO Autopilot",
        status: "running",
        message: `Selecting up to ${limit} opportunities`,
      })
      .select()
      .single();
  try {
    if (settings?.auto_topic_selection) {
      const { data: keywords } = await service
        .from("seo_keywords")
        .select("keyword,current_position,volume")
        .order("volume", { ascending: false })
        .limit(100);
      if (keywords?.length)
        await service.from("seo_topics").upsert(
          keywords.map((keyword: any) => ({
            keyword: keyword.keyword,
            intent: "informational",
            target_location: "Malta",
            priority: Math.max(
              1,
              Math.min(
                100,
                Math.round(100 - Number(keyword.current_position || 50)),
              ),
            ),
            status: "idea",
            suggested_title: keyword.keyword.replace(/\b\w/g, (c: string) =>
              c.toUpperCase(),
            ),
            notes: `Search Console opportunity · ${keyword.volume || 0} impressions · position ${keyword.current_position || "—"}`,
          })),
          { onConflict: "keyword,target_location", ignoreDuplicates: true },
        );
    }
    const statuses = settings?.auto_topic_selection
        ? ["approved", "idea"]
        : ["approved"],
      topicQuery = service
        .from("seo_topics")
        .select("*")
        .in("status", statuses)
        .order("priority", { ascending: false })
        .limit(limit * 2),
      { data: topics, error } = await (campaignId
        ? topicQuery.eq("campaign_id", campaignId)
        : topicQuery);
    if (error) throw error;
    const created = [];
    for (const topic of topics || []) {
      if (created.length >= limit) break;
      const { data: campaign } = topic.campaign_id
        ? await service
            .from("seo_campaigns")
            .select("*")
            .eq("id", topic.campaign_id)
            .maybeSingle()
        : { data: null };
      if (campaign && (!campaign.auto_generate || campaign.status !== "active"))
        continue;
      if (campaign) {
        const monthStart = `${new Date().toISOString().slice(0, 7)}-01T00:00:00.000Z`;
        const { count: monthlyCount } = await service
          .from("seo_articles")
          .select("id", { count: "exact", head: true })
          .eq("campaign_id", campaign.id)
          .gte("created_at", monthStart)
          .neq("status", "rejected");
        if ((monthlyCount || 0) >= Number(campaign.articles_per_month || 1))
          continue;
      }
      const { data: duplicate } = await service
        .from("seo_articles")
        .select("id")
        .eq("focus_keyword", topic.keyword)
        .neq("status", "rejected")
        .limit(1);
      if (duplicate?.length) continue;
      const content = await generate({
          action: "article",
          title: topic.suggested_title,
          keyword: topic.keyword,
          tone: "professional",
          language: "English",
          target_words: campaign?.target_words || 1200,
        }),
        { social_posts, ...articleContent } = content,
        { data: article, error: articleError } = await service
          .from("seo_articles")
          .insert({
            ...articleContent,
            social_copy: social_posts || {},
            focus_keyword: topic.keyword,
            topic_id: topic.id,
            service_id: topic.service_id,
            campaign_id: topic.campaign_id,
            status: "generated",
            language: "English",
            author_name: campaign?.author_name || "Outreach Recruitment",
            auto_selected: topic.status !== "approved",
          })
          .select("id,title")
          .single();
      if (articleError) throw articleError;
      if (settings?.auto_social_drafts && social_posts)
        for (const [platform, post] of Object.entries(social_posts))
          await service.from("seo_social_posts").upsert(
            {
              article_id: article.id,
              platform,
              content: String(post),
              status: "review",
            },
            { onConflict: "article_id,platform" },
          );
      await service
        .from("seo_topics")
        .update({ status: "drafted", updated_at: new Date().toISOString() })
        .eq("id", topic.id);
      created.push(article);
    }
    await service
      .from("seo_automation_logs")
      .update({
        status: "success",
        ended_at: new Date().toISOString(),
        message: created.length
          ? `Generated ${created.length} review-ready draft(s)`
          : "No unused opportunities",
        updated_at: new Date().toISOString(),
      })
      .eq("id", log.data?.id);
    return json({ created, approval_required: true });
  } catch (e) {
    await service
      .from("seo_automation_logs")
      .update({
        status: "failed",
        ended_at: new Date().toISOString(),
        error_details: e instanceof Error ? e.message : "Unknown error",
        updated_at: new Date().toISOString(),
      })
      .eq("id", log.data?.id);
    throw e;
  }
}
async function generate(input: any) {
  const month = new Date().toISOString().slice(0, 7),
    { data: budget } = await service
      .from("seo_api_budgets")
      .select("*")
      .eq("month", month)
      .maybeSingle();
  const targetWords = Math.max(
    800,
    Math.min(Number(input.target_words) || 1200, 2000),
  );
  const prompt = `Create an accurate original ${input.language || "English"} SEO article of approximately ${targetWords} words for Outreach Recruitment. Title: ${input.title}. Focus keyword: ${input.keyword}. Never invent business facts. Return JSON with title, slug, excerpt, seo_title, meta_description, body in Markdown with H2/H3, faqs, internal_links using only real outreachrecruitment.net URLs, suggested_image_prompt for a branded 1200x630 image, and social_posts containing linkedin, facebook, instagram, x and newsletter copy. Include introduction, useful sections, FAQ, conclusion and CTA.`;
  let result: any = null;
  const failures: string[] = [];
  if (Deno.env.get("GEMINI_API_KEY")) {
    try {
      result = await generateGemini(prompt);
    } catch (error) {
      failures.push(
        `Gemini: ${error instanceof Error ? error.message : error}`,
      );
    }
  }
  if (!result && Deno.env.get("GROQ_API_KEY")) {
    try {
      result = await generateGroq(prompt);
    } catch (error) {
      failures.push(`Groq: ${error instanceof Error ? error.message : error}`);
    }
  }
  const openAIAllowed =
    Deno.env.get("OPENAI_API_KEY") &&
    !(
      budget?.hard_stop &&
      Number(budget.current_spend) + Number(budget.reserved_spend) >=
        Number(budget.monthly_limit)
    );
  if (!result && openAIAllowed) {
    try {
      result = await generateOpenAI(prompt);
    } catch (error) {
      failures.push(
        `OpenAI: ${error instanceof Error ? error.message : error}`,
      );
    }
  }
  if (!result) {
    if (failures.length)
      await service.from("seo_automation_logs").insert({
        job_name: "AI provider fallback",
        status: "skipped",
        message: `${failures.join(" | ")} | Used built-in generator`,
        ended_at: new Date().toISOString(),
      });
    return freeContent(input.title, input.keyword, targetWords);
  }
  const { content, provider, model, inputTokens, outputTokens, cost } = result;
  await service.from("seo_api_usage").insert({
    provider,
    model,
    action: input.action || "article",
    input_tokens: inputTokens || 0,
    output_tokens: outputTokens || 0,
    cost,
  });
  if (cost > 0)
    await service
      .from("seo_api_budgets")
      .update({
        current_spend: Number(budget?.current_spend || 0) + cost,
        updated_at: new Date().toISOString(),
      })
      .eq("month", month);
  return content;
}
function parseModelJson(value: string) {
  const cleaned = String(value || "")
    .trim()
    .replace(/^```(?:json)?\s*/i, "")
    .replace(/\s*```$/, "");
  const content = JSON.parse(cleaned);
  for (const field of [
    "title",
    "slug",
    "seo_title",
    "meta_description",
    "body",
  ])
    if (!content[field]) throw new Error(`Response missing ${field}`);
  return content;
}
async function generateGemini(prompt: string) {
  const model = Deno.env.get("GEMINI_MODEL") || "gemini-2.5-flash";
  const response = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${encodeURIComponent(Deno.env.get("GEMINI_API_KEY")!)}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{ role: "user", parts: [{ text: prompt }] }],
        generationConfig: {
          responseMimeType: "application/json",
          temperature: 0.6,
          maxOutputTokens: 8192,
        },
      }),
    },
  );
  const raw = await response.json();
  if (!response.ok)
    throw new Error(raw.error?.message || `HTTP ${response.status}`);
  return {
    content: parseModelJson(raw.candidates?.[0]?.content?.parts?.[0]?.text),
    provider: "google",
    model,
    inputTokens: raw.usageMetadata?.promptTokenCount || 0,
    outputTokens: raw.usageMetadata?.candidatesTokenCount || 0,
    cost: 0,
  };
}
async function generateGroq(prompt: string) {
  const model = Deno.env.get("GROQ_MODEL") || "openai/gpt-oss-20b";
  const response = await fetch(
    "https://api.groq.com/openai/v1/chat/completions",
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${Deno.env.get("GROQ_API_KEY")}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model,
        messages: [{ role: "user", content: prompt }],
        response_format: { type: "json_object" },
        temperature: 0.6,
        max_completion_tokens: 8000,
      }),
    },
  );
  const raw = await response.json();
  if (!response.ok)
    throw new Error(raw.error?.message || `HTTP ${response.status}`);
  return {
    content: parseModelJson(raw.choices?.[0]?.message?.content),
    provider: "groq",
    model,
    inputTokens: raw.usage?.prompt_tokens || 0,
    outputTokens: raw.usage?.completion_tokens || 0,
    cost: 0,
  };
}
async function generateOpenAI(prompt: string) {
  const model = Deno.env.get("OPENAI_MODEL") || "gpt-5-mini";
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${Deno.env.get("OPENAI_API_KEY")}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model,
      input: prompt,
      text: { format: { type: "json_object" } },
    }),
  });
  const raw = await response.json();
  if (!response.ok)
    throw new Error(raw.error?.message || `HTTP ${response.status}`);
  const output = raw.output
    ?.flatMap((item: any) => item.content || [])
    .find((item: any) => item.type === "output_text")?.text;
  return {
    content: parseModelJson(output),
    provider: "openai",
    model,
    inputTokens: raw.usage?.input_tokens || 0,
    outputTokens: raw.usage?.output_tokens || 0,
    cost: Number(Deno.env.get("AI_ESTIMATED_COST_PER_REQUEST") || "0.03"),
  };
}
function freeContent(title: string, keyword: string, target = 1200) {
  const articleTitle = title || `A Practical Guide to ${keyword}`;
  const sections = [
    `## Introduction\n\nPeople researching **${keyword}** need clear, practical information before deciding what to do next. This guide explains useful preparation steps and questions to ask without promising a particular employment, study or immigration outcome.`,
    `## Define Your Goal\n\nStart by identifying the opportunity you want, the experience you can demonstrate and the location that suits you. Review every description carefully and compare its requirements with your real skills, qualifications and availability.`,
    `## Research Reliable Sources\n\nUse reputable sources and confirm important requirements with the employer or appropriate official authority. Rules and availability can change, so avoid relying only on old posts or unsupported claims.`,
    `## Prepare Carefully\n\nAdapt your information to the opportunity, use clear examples and check that your contact details are correct. Keep a tracker containing deadlines, documents submitted and follow-up dates.`,
    `## Useful Outreach Recruitment Resources\n\nReview current opportunities at https://outreachrecruitment.net/jobs/ and practical guidance at https://outreachrecruitment.net/news-updates. Follow the official application instructions shown on each page.`,
    `## Frequently Asked Questions\n\n### Does applying guarantee an interview or offer?\n\nNo. Applications are assessed against each opportunity and no legitimate service can guarantee selection.\n\n### Should important legal information be verified?\n\nYes. Confirm visa, study and work-permit matters with the relevant official authority because rules depend on individual circumstances and may change.`,
    `## Conclusion\n\nA successful approach to **${keyword}** begins with reliable research, an honest application and realistic expectations. Verify important information and take each step only when you have enough evidence.`,
  ];
  const extras = [
    "Create a written checklist and record what you learn before continuing.",
    "Prepare specific examples that demonstrate relevant experience instead of making broad claims.",
    "Keep sensitive documents secure and use only official, verified submission channels.",
    "Review your professional profile and ensure it is consistent with your application.",
  ];
  let body = sections.join("\n\n"),
    i = 0;
  while (body.split(/\s+/).length < target - 50) {
    body += `\n\n### Practical action ${i + 1}\n\n${extras[i % extras.length]} Relate this action directly to ${keyword} and review the result before moving forward.`;
    i++;
  }
  return {
    title: articleTitle,
    slug: articleTitle
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, ""),
    excerpt: `A practical guide to ${keyword}, including research, preparation and reliable next steps.`,
    seo_title: `${articleTitle} | Outreach Recruitment`,
    meta_description: `Learn about ${keyword} with practical preparation steps and reliable resources from Outreach Recruitment.`,
    body,
    suggested_image_prompt: `Professional editorial photograph for ${articleTitle}, Malta setting, natural blue accents, no text, 1200 × 630 pixels.`,
    faqs: [],
    internal_links: [
      "https://outreachrecruitment.net/jobs/",
      "https://outreachrecruitment.net/news-updates",
    ],
    social_posts: {
      linkedin: `New guide: ${articleTitle}. Read practical advice from Outreach Recruitment.`,
      facebook: `Looking for reliable information about ${keyword}? Read our new practical guide.`,
      instagram: `New guide: ${articleTitle} #Malta #OutreachRecruitment`,
      x: `New guide: ${articleTitle} — practical information from Outreach Recruitment.`,
      newsletter: `New this week: ${articleTitle}. Explore practical steps and reliable resources.`,
    },
  };
}
function json(value: unknown, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
