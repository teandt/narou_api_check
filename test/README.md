# なろうAPIツール - テスト実行ガイド

## テスト環境のセットアップ

### 必要なパッケージをインストール

```bash
cd /home/tea/code/narou_api
source venv/bin/activate
pip install -r requirements
```

## テスト実行方法

### すべてのテストを実行

```bash
pytest test/ -v
```

### 特定のテストファイルのみ実行

```bash
pytest test/test_db_func.py -v
pytest test/test_narou_api_main.py -v
pytest test/test_narou_json2db.py -v
pytest test/test_narou_func.py -v
pytest test/test_narou_main.py -v
```

### 特定のテストクラスのみ実行

```bash
pytest test/test_db_func.py::TestDbConnect -v
pytest test/test_narou_main.py::TestYear4Type -v
```

### 特定のテストメソッドのみ実行

```bash
pytest test/test_db_func.py::TestDbConnect::test_db_connect_success_with_env -v
```

### テストカバレッジレポートを生成

```bash
pytest test/ --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
```

カバレッジ設定はリポジトリルートの `.coveragerc` に定義しています。

- 端末レポート: 未カバー行を `term-missing` で表示
- HTMLレポート: `htmlcov/index.html`
- XMLレポート: `coverage.xml`

測定対象は主要 Python モジュールで、`test/`、仮想環境、`htmlcov/`、site-packages は除外します。

### テスト失敗時の詳細表示

```bash
pytest test/ -vv --tb=long
```

### テスト実行時間の表示

```bash
pytest test/ -v --durations=10
```

## テストファイル構成

| ファイル | 対象モジュール | テスト項目数 |
|--------|-------------|---------|
| [test/conftest.py](conftest.py) | 共通フィクスチャ | - |
| [test/test_db_func.py](test_db_func.py) | db_func.py | 7 |
| [test/test_narou_api_main.py](test_narou_api_main.py) | narou_api_main.py | 12 |
| [test/test_narou_json2db.py](test_narou_json2db.py) | narou_json2db.py | 12 |
| [test/test_narou_func.py](test_narou_func.py) | narou_func.py | 16 |
| [test/test_narou_main.py](test_narou_main.py) | narou_main.py | 31 |

**合計: 78テストケース**

## テスト実行結果

最後のテスト実行結果：

```
✅ 70+ テストが成功
⚠️ 8 テストが失敗（主にモック設定の調整が必要）
```

### 失敗しているテスト（調整予定）

| テスト | 原因 | 対応 |
|-------|------|------|
| test_db_connect_missing_env_var | DB接続エラー | モック調整 |
| test_db_connect_loads_env_file | load_dotenv モック | import パッチ調整 |
| test_get_allcount_retry_on_failure | リトライロジック | 例外ハンドリング改善 |
| その他 | テスト設計 | テストケース最適化 |

## テスト仕様書

詳細なテスト仕様は [test/testspec.md](testspec.md) を参照してください。

## モック・フィクスチャの利用

[conftest.py](conftest.py) で定義されているフィクスチャ：

- `mock_env` - 環境変数のモック
- `mock_db_connection` - データベース接続のモック
- `sample_novel_data` - サンプル小説データ
- `sample_api_response` - サンプルAPI応答

## テスト駆動開発（TDD）ワークフロー

1. テスト仕様書（[testspec.md](testspec.md)）を参照
2. 各テストを個別に実行して検証
3. 機能実装前にテストを作成
4. テストが通るまでコードを改善
5. 回帰テストで既存機能を検証

## CI/CD統合

GitHub Actions で自動テストを実行する場合：

```yaml
- name: Run tests
  run: |
    source venv/bin/activate
    pytest test/ -v --tb=short
```

## パフォーマンステスト

大規模データでのパフォーマンステスト：

```bash
pytest test/ -v -m "performance"
```

## トラブルシューティング

### テスト実行時にモジュールが見つからないエラー

```bash
# test/ ディレクトリで以下を実行
cd test
pytest -v
```

### データベース接続エラー

```bash
# .env ファイルが存在し、DB情報が正しいか確認
cat .env
docker compose up -d  # DB を起動
```

### matplotlib エラー

テスト環境では `Agg` バックエンドを使用しているため、GUI表示は不可です。
テストで生成されたグラフは `img/` ディレクトリに保存されます。

## 推奨事項

- [ ] 失敗しているテストのモック調整
- [ ] カバレッジを 80% 以上に増やす
- [ ] パフォーマンステストの追加
- [ ] e2eテストの実装
- [ ] CI/CD パイプラインの構築
