# STATUS VERIFIKASI ENDPOINT RPC

Diuji pada sesi setup. Semua baris di bawah adalah hasil eksekusi nyata,
bukan asumsi dari dokumentasi.

## EVM — `eth_chainId`

| Rantai | Endpoint | chainId | Status |
|---|---|---|---|
| Ethereum | ethereum-rpc.publicnode.com | `0x1` | PASS |
| Arbitrum One | arbitrum-one-rpc.publicnode.com | `0xa4b1` | PASS |
| Optimism | optimism-rpc.publicnode.com | `0xa` | PASS |
| Base | base-rpc.publicnode.com | `0x2105` | PASS |
| Polygon | polygon-bor-rpc.publicnode.com | `0x89` | PASS |
| BSC | bsc-rpc.publicnode.com | `0x38` | PASS |
| Avalanche C-Chain | avalanche-c-chain-rpc.publicnode.com | `0xa86a` | PASS |
| Gnosis | gnosis-rpc.publicnode.com | `0x64` | PASS |
| Sepolia | ethereum-sepolia-rpc.publicnode.com | `0xaa36a7` | PASS |

## Tron — `eth_chainId` (JSON-RPC gateway)

| Endpoint | chainId | Status |
|---|---|---|
| api.trongrid.io/jsonrpc | `0x2b6653dc` | PASS |

## Solana — `getHealth`

| Endpoint | Result | Status |
|---|---|---|
| api.mainnet-beta.solana.com | `ok` | PASS |

## TON — `getMasterchainInfo`

| Endpoint | Result | Status |
|---|---|---|
| toncenter.com/api/v2 | `ok:true`, seqno terisi | PASS |

## Aptos — REST `/v1`

| Endpoint | Result | Status |
|---|---|---|
| fullnode.mainnet.aptoslabs.com/v1 | `chain_id:1`, ledger terisi | PASS |

## Sui — GAGAL (perubahan infrastruktur hulu)

| Endpoint | Result | Status |
|---|---|---|
| fullnode.mainnet.sui.io | `-32601: public JSON-RPC deprecated` | FAIL |
| sui-rpc.publicnode.com | `-32000: deprecated` | FAIL |

**Kesimpulan Sui:** Sui mematikan JSON-RPC publik dan bermigrasi ke gRPC.
Implikasi untuk Fase 3:
- `sui move test` **tetap bisa** dijalankan — tidak butuh RPC sama sekali.
- Tier 6 "fork state Sui nyata" **butuh** endpoint gRPC milik sendiri
  (atau provider berbayar). Ini bukan cacat setup, ini perubahan hulu.

## FORK MAINNET — UJI END-TO-END

```
anvil --fork-url https://ethereum-rpc.publicnode.com --port 8546
  block-number : 26296555
  chain-id     : 1
  WETH  totalSupply : 2217498675629032213087801  (2.217e24)
  USDC  symbol      : "USDC"
```

Artinya: fork benar-benar menarik state mainnet (block 26.296.555) dan bisa
membaca state kontrak nyata (WETH, USDC). Tanpa `--broadcast`, tidak ada
transaksi keluar.

## Catatan Operasional

1. Endpoint `publicnode.com` adalah layanan gratis tanpa SLA. Rate limit bisa
   memicu kegagalan fuzzing yang panjang — bila itu terjadi, ulangi dengan
   `--compute-units-per-second` yang lebih rendah atau ganti provider.
2. Tidak ada API key di file ini. Semua endpoint no-key termasuk dalam
   kategori aman untuk `.env.rpc` yang di-commit.
3. Jangan pernah menambahkan private key berisi dana nyata ke file apa pun
   di repo ini.
