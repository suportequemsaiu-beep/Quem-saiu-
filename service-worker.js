/* Quem Saiu — service worker
   1) Receber o arquivo compartilhado pelo Android (Web Share Target) e guardá-lo
      temporariamente para a página ler. Nada disso sai do aparelho.
   2) Mostrar o aviso de lembrete, SE a pessoa ligou os avisos. O aviso chega sem conteúdo
      nenhum: o texto abaixo é fixo e fica aqui, neste arquivo. */

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

/* ---------- aviso de lembrete (só chega para quem ligou os avisos) ---------- */
self.addEventListener("push", function (evento) {
  evento.waitUntil(
    self.registration.showNotification("Quem Saiu", {
      body: "Seu arquivo do Instagram pode estar pronto. Toque para mandar a lista.",
      icon: "icone-192.png",
      badge: "icone-192.png",
      tag: "quemsaiu-aviso",
      data: { url: "./?aviso=1" }
    })
  );
});

self.addEventListener("notificationclick", function (evento) {
  evento.notification.close();
  evento.waitUntil(
    (async function () {
      var janelas = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
      for (var i = 0; i < janelas.length; i++) {
        if ("focus" in janelas[i]) return janelas[i].focus();
      }
      return self.clients.openWindow("./?aviso=1");
    })()
  );
});
