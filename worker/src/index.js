import {serveNews} from "./news-route.js";
export default {
  async fetch(request, env, ctx) {
    const url=new URL(request.url);
    if (request.method==="GET" && url.pathname==="/news.csv") return serveNews(request,env,ctx);
    if (url.pathname==="/health") return Response.json({ok:true,service:"barreplay-news"});
    // For a standalone deployment, all other routes are absent. If this code
    // is merged into the existing BarReplay data Worker, keep its current
    // router here after the /news.csv branch.
    return new Response("Not found",{status:404});
  }
};
