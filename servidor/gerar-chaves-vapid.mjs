// Gera o par de chaves que identifica o Quem Saiu perante os serviços de aviso (Web Push / VAPID).
// Uso:  node gerar-chaves-vapid.mjs
// - VAPID_PUBLICA: vai no servidor (segredo) E no script.js (AVISOS_CHAVE_PUBLICA). Pode ser pública.
// - VAPID_PRIVADA_JWK: vai SÓ no servidor (segredo). Nunca coloque no repositório.
import { generateKeyPairSync } from "node:crypto";

const { publicKey, privateKey } = generateKeyPairSync("ec", { namedCurve: "P-256" });
const jwkPriv = privateKey.export({ format: "jwk" });
const jwkPub = publicKey.export({ format: "jwk" });
const b64u = (b) => Buffer.from(b).toString("base64url");
const ponto = Buffer.concat([Buffer.from([4]), Buffer.from(jwkPub.x, "base64url"), Buffer.from(jwkPub.y, "base64url")]);

console.log("VAPID_PUBLICA=" + b64u(ponto));
console.log("VAPID_PRIVADA_JWK=" + JSON.stringify({ kty: "EC", crv: "P-256", x: jwkPriv.x, y: jwkPriv.y, d: jwkPriv.d }));
