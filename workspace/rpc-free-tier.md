# RPC Free Tier — Terverifikasi

**Verifikasi terakhir:** 2026-11-03 · metode: `cast rpc eth_chainId` per endpoint (EVM) dan probe HTTP (non-EVM).
**Hasil: 20/20 EVM + 1 fallback-cari + 4 non-EVM = semua PASS.**

> Dokumen ini **hanya memuat endpoint publik tanpa API key**. Endpoint ber-kredensial disimpan di
> `.env.rpc.secret` (di-ignore git, local VPS only) dan dimuat otomatis oleh `rpc-env.sh`.

---

## 1. EVM — `eth_chainId` PASS

| Rantai | chainId | Endpoint | Provider |
|---|---|---|---|
| Ethereum | `1` | `https://ethereum-rpc.publicnode.com` | PublicNode |
| Arbitrum One | `42161` | `https://arbitrum-one-rpc.publicnode.com` | PublicNode |
| Optimism | `10` | `https://optimism-rpc.publicnode.com` | PublicNode |
| Base | `8453` | `https://base-rpc.publicnode.com` | PublicNode |
| Polygon | `137` | `https://polygon-bor-rpc.publicnode.com` | PublicNode |
| BSC | `56` | `https://bsc-rpc.publicnode.com` | PublicNode |
| Avalanche C-Chain | `43114` | `https://avalanche-c-chain-rpc.publicnode.com` | PublicNode |
| Gnosis | `100` | `https://gnosis-rpc.publicnode.com` | PublicNode |
| Sepolia (testnet) | `11155111` | `https://ethereum-sepolia-rpc.publicnode.com` | PublicNode |
| Linea | `59144` | `https://linea-rpc.publicnode.com` | PublicNode |
| zkSync Era | `324` | `https://mainnet.era.zksync.io` | Matter Labs |
| Scroll | `534352` | `https://scroll-rpc.publicnode.com` | PublicNode |
| Unichain | `130` | `https://unichain-rpc.publicnode.com` | PublicNode |
| Ink | `57073` | `https://ink-rpc.publicnode.com` | PublicNode |
| Soneium | `1868` | `https://soneium-rpc.publicnode.com` | PublicNode |
| Mantle | `5000` | `https://mantle-rpc.publicnode.com` | PublicNode |
| Celo | `42220` | `https://celo-rpc.publicnode.com` | PublicNode |
| World Chain | `480` | `https://worldchain-mainnet.g.alchemy.com/public` | Alchemy public |
| Blast | `81457` | `https://rpc.blast.io` | Blast resmi |
| HyperEVM | `999` | `https://rpc.hyperliquid.xyz/evm` | Hyperliquid resmi |

### Slug yang SALAH (jangan dipakai — 404/503)

`blast-rpc.publicnode.com` (503) · `lisk-rpc.publicnode.com` (404) · `mode-rpc.publicnode.com` (404) ·
`zora-rpc.publicnode.com` (404). Ini sempat membuat endpoint dinyatakan "mati" padahal providernya hidup
dengan hostname lain — sebab itu jangan menyimpulkan endpoint mati dari satu hostname saja.

### Rantai yang punya endpoint tapi lambat/jarang: Lisk, Mode, Zora

| Rantai | chainId | Endpoint (semua PASS) |
|---|---|---|
| Lisk | `1135` | `https://rpc.api.lisk.com` · `https://lisk.drpc.org` |
| Mode | `34443` | `https://mainnet.mode.network` · `https://mode.drpc.org` · `https://1rpc.io/mode` |
| Zora | `7777777` | `https://rpc.zora.energy` · `https://zora.drpc.org` |

---

## 2. Non-EVM

| Rantai | Endpoint | Metode uji | Hasil |
|---|---|---|---|
| TRON | `https://api.trongrid.io/jsonrpc` (chainId `0x2b6653dc`) | `eth_chainId` | PASS |
| TRON (HTTP API) | `https://api.trongrid.io` | `wallet/getnowblock` | PASS |
| Solana | `https://api.mainnet-beta.solana.com` | `getHealth` | `ok` |
| TON | `https://toncenter.com/api/v2` | `getMasterchainInfo` | `ok:true`, seqno terisi |
| TON (indexer) | `https://toncenter.com/api/v3` | — | PASS (v3) |
| Aptos | `https://fullnode.mainnet.aptoslabs.com/v1` | REST `/v1` | `chain_id: 1` |
| Sui | — | — | **GAGAL**: JSON-RPC publik deprecated, wajib gRPC |

**Sui:** `fullnode.mainnet.sui.io` → `-32601 public JSON-RPC deprecated`; `sui-rpc.publicnode.com` → `-32000 deprecated`.
`sui move test` tetap jalan tanpa RPC. Fork state Sui butuh endpoint gRPC sendiri.

---

## 3. Batasan yang wajib diingat

1. **Archive tidak tersedia.** PublicNode menolak `eth_getLogs` historis: `-32602 "Archive requests require a
   personal token"`. Untuk log lama pakai provider berbayar, atau chunking di blok terdekat.
2. **`eth_call` boleh menipu.** Revert dengan `data: "0x"` muncul untuk **selector yang ada maupun yang tidak ada**
   pada endpoint ini. Jangan pakai `revert 0x` sebagai bukti "fungsi tidak ada" — pakai scan dispatcher
   `eth_getCode` (`PUSH4..EQ`) atau decoded-call sentinel. Lihat `VERDICT.md` Langkah 0.
3. **Tanpa SLA.** Rate limit bisa menggagalkan fuzzing panjang; turunkan `--compute-units-per-second`
   atau pindah provider.
4. **Jangan pernah** menaruh private key berisi dana nyata di file apa pun di repo ini.