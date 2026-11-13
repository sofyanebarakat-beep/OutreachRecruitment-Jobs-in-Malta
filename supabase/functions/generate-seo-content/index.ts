import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const cors={"Access-Control-Allow-Origin":"*","Access-Control-Allow-Headers":"authorization, x-client-info, apikey, content-type"};
Deno.serve(async(req)=>{
  if(req.method==="OPTIONS")return new Response("ok",{headers:cors});
  try{
    const auth=req.headers.get("Authorization")||"";
    const admin=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_ANON_KEY")!,{global:{headers:{Authorization:auth}}});
    const {data:isAdmin}=await admin.rpc("is_admin");
    if(!isAdmin)return json({error:"Administrator access required"},403);
    const service=createClient(Deno.env.get("SUPABASE_URL")!,Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!);
    const month=new Date().toISOString().slice(0,7),{data:budget}=await service.from("seo_api_budgets").select("*").eq("month",month).maybeSingle();
    if(budget?.hard_stop&&Number(budget.current_spend)+Number(budget.reserved_spend)>=Number(budget.monthly_limit))return json({error:"Monthly AI budget exhausted"},402);
    const input=await req.json(),apiKey=Deno.env.get("OPENAI_API_KEY");
    if(!apiKey)return json({error:"OPENAI_API_KEY is not configured"},503);
    const prompt=`Write an accurate, original ${input.language||"English"} SEO article for Outreach Recruitment. Title: ${input.title}. Focus keyword: ${input.keyword}. Tone: ${input.tone||"professional"}. Do not invent business facts. Return JSON only with title, slug, excerpt, seo_title, meta_description, body (Markdown with H2/H3), faqs, and internal_links. Include an introduction, useful sections, FAQs, conclusion and a relevant call to action.`;
    const res=await fetch("https://api.openai.com/v1/responses",{method:"POST",headers:{Authorization:`Bearer ${apiKey}`,"Content-Type":"application/json"},body:JSON.stringify({model:Deno.env.get("OPENAI_MODEL")||"gpt-5-mini",input:prompt,text:{format:{type:"json_object"}}})});
    const raw=await res.json();if(!res.ok)throw new Error(raw.error?.message||"AI request failed");
    const text=raw.output?.flatMap((x:any)=>x.content||[]).find((x:any)=>x.type==="output_text")?.text;
    const content=JSON.parse(text||"{}");
    const usage=raw.usage||{},cost=Number(Deno.env.get("AI_ESTIMATED_COST_PER_REQUEST")||"0.03");
    await service.from("seo_api_usage").insert({provider:"openai",model:Deno.env.get("OPENAI_MODEL")||"gpt-5-mini",action:input.action||"article",input_tokens:usage.input_tokens||0,output_tokens:usage.output_tokens||0,cost});
    await service.from("seo_api_budgets").update({current_spend:Number(budget?.current_spend||0)+cost,updated_at:new Date().toISOString()}).eq("month",month);
    return json(content,200);
  }catch(e){return json({error:e instanceof Error?e.message:"Unknown error"},500)}
});
function json(value:unknown,status=200){return new Response(JSON.stringify(value),{status,headers:{...cors,"Content-Type":"application/json"}})}
