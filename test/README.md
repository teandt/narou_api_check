# なろうAPIツール - テストガイド

このディレクトリには、なろうAPIツールの単体テストとテスト仕様書を配置しています。
テストの詳細な観点は [testspec.md](testspec.md) を参照してください。

## テスト環境のセットアップ

リポジトリルートで仮想環境を有効化し、依存パッケージをインストールします。

```bash
cd /home/tea/code/narou_api
source venv/bin/activate
python3 -m pip install -r requirements
```

`requirements` には `pytest`、`pytest-cov`、`pytest-mock`、`coverage` も含まれています。

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

### テスト失敗時の詳細表示

```bash
pytest test/ -vv --tb=long
```

### テスト実行時間の表示

```bash
pytest test/ -v --durations=10
```

## カバレッジ

カバレッジ設定はリポジトリルートの `.coveragerc` に定義しています。

```bash
pytest test/ --cov=. --cov-report=term-missing --cov-report=html --cov-report=xml
```

- 端末レポート: 未カバー行を `term-missing` で表示
- HTMLレポート: `htmlcov/index.html`
- XMLレポート: `coverage.xml`

測定対象はリポジトリルート配下の Python モジュールです。
`test/`、`venv/`、`.venv/`、`htmlcov/`、site-packages は除外します。

## テストファイル構成

| ファイル | 対象モジュール | 主な確認内容 | テスト数 |
|--------|-------------|------------|--------|
| [conftest.py](conftest.py) | 共通フィクスチャ | 環境変数、DB接続、サンプルデータ、API応答 | - |
| [test_db_func.py](test_db_func.py) | `db_func.py` | DB接続設定、文字セット、DictCursor、ポート不正、接続エラー、`.env`読み込み | 6 |
| [test_narou_api_main.py](test_narou_api_main.py) | `narou_api_main.py` | allcount取得、リトライ、カウンター確認、出力ファイル指定、JSON形式、重複排除、UTF-8 | 12 |
| [test_narou_json2db.py](test_narou_json2db.py) | `narou_json2db.py` | カウンター確認、引数解析、登録行生成、1000件バッチ、入力ファイル指定、ロールバック | 13 |
| [test_narou_func.py](test_narou_func.py) | `narou_func.py` | カウンター確認、ヒストグラム、タイトル長平均、連載/短編数、グラフ出力パス | 16 |
| [test_narou_main.py](test_narou_main.py) | `narou_main.py` | 年指定バリデーション、引数解析、各オプションの入力検証、関数呼び出し、エラー処理 | 27 |

**合計: 74テストケース**

テスト数を確認する場合は、次のように実ファイルから数えられます。

```bash
rg -c "^    def test_" test/test_*.py
```

## 共通フィクスチャ

[conftest.py](conftest.py) で以下のフィクスチャを定義しています。

- `mock_env` - DB接続用の環境変数を設定
- `mock_db_connection` - DB接続オブジェクトとカーソルのモック
- `sample_novel_data` - 小説データのサンプル
- `sample_api_response` - なろうAPI応答のサンプル

テストは外部APIや実DBへ直接接続せず、`unittest.mock.patch` と共通フィクスチャで依存先を差し替える構成です。

## テスト対象の概要

- `db_func.py`: `.env` と環境変数を使った MySQL 接続
- `narou_api_main.py`: なろうAPIからの件数取得、JSON出力、カウンター確認
- `narou_json2db.py`: JSON入力、DB登録用データ生成、バッチ登録、トランザクション処理
- `narou_func.py`: DB取得結果を使った統計処理とグラフ出力
- `narou_main.py`: コマンドライン引数の解釈と各処理関数の呼び出し

## 注意点

- `test_narou_func.py` は matplotlib のバックエンドに `Agg` を使用します。
- グラフ生成処理は `plt.savefig` や `plt.show` をモックして検証しています。
- 実DBを使った結合テストや、なろうAPIへの実通信テストはこのテスト群には含まれていません。
- `pytest -m "performance"` で実行できる performance マーカー付きテストは現時点では定義されていません。

## トラブルシューティング

### モジュールが見つからない

リポジトリルートから実行してください。

```bash
cd /home/tea/code/narou_api
pytest test/ -v
```

各テストファイルでは親ディレクトリを `sys.path` に追加して、ルート直下のモジュールを import しています。

### DB接続エラー

通常の単体テストではDB接続をモックします。
実DBを使って手動確認する場合は、`.env` のDB設定と Docker Compose の起動状態を確認してください。

```bash
docker compose up
```

### matplotlib のGUI表示

テストではGUI表示を使わず、`Agg` バックエンドで検証します。
そのため、テスト実行中にグラフ画面は表示されません。

## テスト追加時の目安

1. 既存の対象モジュールに近いテストファイルへ追加する。
2. 外部API、DB、ファイルI/O、グラフ出力は必要に応じてモックする。
3. 仕様レベルの観点を追加した場合は [testspec.md](testspec.md) も更新する。
4. 実行コマンドとテスト数が変わる場合は、このREADMEも更新する。
