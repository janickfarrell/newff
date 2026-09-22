export async function serveNews(request, env, ctx) {
  if (!env.HF_REPO_ID) return new Response("HF_REPO_ID is not configured", {status: 500});
  const revision = env.HF_REVISION || "main";
  const upstream = `https://huggingface.co/datasets/${env.HF_REPO_ID}/resolve/${revision}/news.csv`;
  const cache = caches.default;
  const cacheKey = new Request(new URL("/__barreplay_cache/news.csv", request.url), {method:"GET"});
  const cached = await cache.match(cacheKey);
  const headers = {"User-Agent":"BarReplay-News-Worker/1.0"};
  if (env.HF_TOKEN) headers.Authorization = `Bearer ${env.HF_TOKEN}`;
  try {
    const response = await fetch(upstream, {headers, cf:{cacheTtl:300, cacheEverything:true}});
    if (!response.ok) throw new Error(`Hugging Face returned ${response.status}`);
    const out = new Response(response.body, {status:200, headers:{"Content-Type":"text/csv; charset=utf-8","Content-Disposition":"attachment; filename=news.csv","Cache-Control":"public, max-age=300","Access-Control-Allow-Origin":"*","X-BarReplay-Source":"huggingface"}});
    ctx.waitUntil(cache.put(cacheKey, out.clone()));
    return out;
  } catch (error) {
    if (cached) {const h=new Headers(cached.headers);h.set("X-BarReplay-Cache","stale");return new Response(cached.body,{status:200,headers:h});}
    return new Response(`News unavailable: ${error.message}`, {status:502});
  }
}
