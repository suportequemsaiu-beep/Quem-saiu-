/* Quem Saiu — service worker
   Função principal: receber o arquivo compartilhado pelo Android
   (Web Share Target) e guardá-lo temporariamente para a página ler.
   Nada é enviado para servidor nenhum: tudo acontece dentro do aparelho. */

var CACHE_COMPARTILHADO = "quemsaiu-compartilhado";

self.addEventListener("install", function () {
  self.skipWaiting();
});

self.addEventListener("activate", function (evento) {
  evento.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", function (evento) {
  var url = new URL(evento.request.url);

  /* O Android envia o arquivo por POST para /receber */
  if (evento.request.method === "POST" && url.pathname.endsWith("/receber")) {
    evento.respondWith(
      (async function () {
        try {
          var form = await evento.request.formData();
          var arquivos = form.getAll("arquivo");

          if (!arquivos || arquivos.length === 0) {
            return Response.redirect("./?compartilhado=vazio", 303);
          }

          var arquivo = arquivos[0];
          var cache = await caches.open(CACHE_COMPARTILHADO);
          await cache.put(
            "arquivo-compartilhado",
            new Response(arquivo, {
              headers: {
                "content-type": arquivo.type || "application/zip",
                "x-nome-arquivo": encodeURIComponent(arquivo.name || "instagram.zip")
              }
            })
          );

          return Response.redirect("./?compartilhado=1", 303);
        } catch (erro) {
          return Response.redirect("./?compartilhado=erro", 303);
        }
      })()
    );
  }
});
