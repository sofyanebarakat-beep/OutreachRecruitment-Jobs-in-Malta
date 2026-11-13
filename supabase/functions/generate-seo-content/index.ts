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
    return input.action === "scheduled_drafts"
      ? await scheduled(Math.max(1, Math.min(Number(input.count) || 2, 5)))
      : json(await generate(input));
  } catch (e) {
    return json(
      { error: e instanceof Error ? e.message : "Unknown error" },
      500,
    );
  }
});
async function scheduled(count: number) {
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
              Math.min(100, Math.round(100 - Number(keyword.current_position || 50))),
            ),
            status: "idea",
            suggested_title: keyword.keyword.replace(/\b\w/g, (c: string) => c.toUpperCase()),
            notes: `Search Console opportunity · ${keyword.volume || 0} impressions · position ${keyword.current_position || "—"}`,
          })),
          { onConflict: "keyword,target_location", ignoreDuplicates: true },
        );
    }
    const statuses = settings?.auto_topic_selection
        ? ["approved", "idea"]
        : ["approved"],
      { data: topics, error } = await service
        .from("seo_topics")
        .select("*")
        .in("status", statuses)
        .order("priority", { ascending: false })
        .limit(limit * 2);
    if (error) throw error;
    const created = [];
    for (const topic of topics || []) {
      if (created.length >= limit) break;
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
            auto_selected: topic.status !== "approved",
          })
          .select("id,title")
          .single();
      if (articleError) throw articleError;
      if (settings?.auto_social_drafts && social_posts)
        for (const [platform, post] of Object.entries(social_posts))
          await service
            .from("seo_social_posts")
            .upsert(
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
  if (
    budget?.hard_stop &&
    Number(budget.current_spend) + Number(budget.reserved_spend) >=
      Number(budget.monthly_limit)
  )
    throw new Error("Monthly AI budget exhausted");
  const key = Deno.env.get("OPENAI_API_KEY");
  if (!key) throw new Error("OPENAI_API_KEY is not configured");
  const prompt = `Create an accurate original ${input.language || "English"} SEO article for Outreach Recruitment. Title: ${input.title}. Focus keyword: ${input.keyword}. Never invent business facts. Return JSON with title, slug, excerpt, seo_title, meta_description, body in Markdown with H2/H3, faqs, internal_links using only real outreachrecruitment.net URLs, suggested_image_prompt for a branded 1200x630 image, and social_posts containing linkedin, facebook, instagram, x and newsletter copy. Include introduction, useful sections, FAQ, conclusion and CTA.`;
  const response = await fetch("https://api.openai.com/v1/responses", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${key}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: Deno.env.get("OPENAI_MODEL") || "gpt-5-mini",
        input: prompt,
        text: { format: { type: "json_object" } },
      }),
    }),
    raw = await response.json();
  if (!response.ok) throw new Error(raw.error?.message || "AI request failed");
  const output = raw.output
      ?.flatMap((x: any) => x.content || [])
      .find((x: any) => x.type === "output_text")?.text,
    content = JSON.parse(output || "{}"),
    usage = raw.usage || {},
    cost = Number(Deno.env.get("AI_ESTIMATED_COST_PER_REQUEST") || "0.03");
  await service
    .from("seo_api_usage")
    .insert({
      provider: "openai",
      model: Deno.env.get("OPENAI_MODEL") || "gpt-5-mini",
      action: input.action || "article",
      input_tokens: usage.input_tokens || 0,
      output_tokens: usage.output_tokens || 0,
      cost,
    });
  await service
    .from("seo_api_budgets")
    .update({
      current_spend: Number(budget?.current_spend || 0) + cost,
      updated_at: new Date().toISOString(),
    })
    .eq("month", month);
  return content;
}
function json(value: unknown, status = 200) {
  return new Response(JSON.stringify(value), {
    status,
    headers: { ...cors, "Content-Type": "application/json" },
  });
}
