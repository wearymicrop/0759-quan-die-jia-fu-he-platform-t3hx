# 券叠加复核台

门店结算员按小票发生时的有效规则复算优惠，对照优惠组合、原始分摊、退款及差额，归档带来源行和版本号的追溯联单。

## 启动

```sh
docker compose up --build
```

访问 `http://localhost:18453`。使用 `docker compose exec -T app pytest -q` 运行测试。宿主可安装 `requirements.txt` 后执行 `pytest -q`。归档数据库存于 Compose 命名卷 `ledger`，执行 `docker compose down -v` 会清空归档。配置见 `.env.example`。

## 复核演练

1. 选「含差异流水」，打开「优惠求解」。小票 `000731` 选择「品类九折」和「店券5」，实付复算为 49.00 元。规则方阵展示哪些组合互斥。
2. 小票 `000732` 的一分钱尾差落给明细 `01`。在「退单冲回」可核对原小票跨日退货，在「金额对账」查看真实收款与复算的分级差异。
3. 选择「保存联单」并打开「追溯联单」，复核原票与退票关联，执行重算并导出证据。
4. 自带数据可从「复核自备流水」粘贴逐行 JSON 与规则集。样例位于 `sample_data/`，字段见 [数据字典](docs/DATA-DICTIONARY.md)。

## 接口

- `GET /api/health` 检查存储连通性。
- `GET /api/samples/clean` 和 `GET /api/samples/dirty` 返回计算结果。七个子路径分别是 `receipts`、`versions`、`eligibility`、`optimizer`、`refunds`、`reconcile`、`trace`。求解支持 `?receipt=000731`，冲回支持 `?event=R001`。
- `POST /api/runs` 接收 `{"sample":"dirty"}` 或 `{"events":"逐行流水","rules":{...}}`。`GET /api/runs/{id}` 查询归档，`POST /api/runs/{id}/rerun` 重算，`GET /api/runs/{id}/export` 下载附件。

## 复算边界

计算以人民币分入账，资格按符合品类的商品原价小计判定。组合中的券按规则顺序施加在当时的明细余额上。每单最多十二张候选券，展示最多十二组排名。退货以原单和明细为锚点，沿原折扣分摊按件冲回。当前范围覆盖整件退货和促销复核，储值支付、税费与运费另计。见 [规则与测试](docs/DEPTH.md)。
