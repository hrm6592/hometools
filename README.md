# Tools

動画ファイルの整理、Transmission の管理、Linux サーバーの運用、World of Tanks の設定などに使う個人用スクリプト集です。Python・Bash・Perl・PowerShell・バッチ・CoffeeScript のツールを、用途ごとに個別に実行します。

古い環境向けのコードや固定パスを含みます。利用するスクリプトの対象フォルダー、接続先、外部コマンドを確認してから実行してください。

## ツール一覧

### 動画の整理・変換

| ファイル | 用途 | 主な前提・動作 |
| --- | --- | --- |
| [check_video.py](check_video.py) | 動画情報を取得し、ファイル名を正規化して SQLite に記録 | MediaInfo、Unix の `syslog`。名前・権限・DB を変更 |
| [check_video.sh](check_video.sh) | 動画形式・高さに応じて拡張子や名前を修正 | MediaInfo。固定のダウンロードフォルダーを処理 |
| [rename_video.sh](rename_video.sh) | 特定の命名規則に合わせて動画をリネーム | MediaInfo。処理先とコマンドのパスは固定 |
| [sulvage_mp4.plx](sulvage_mp4.plx) | サブフォルダーの動画をリネームして親フォルダーへ移動 | MediaInfo、`Term::ExtendedColor`。処理後に元フォルダーを削除。`-t` で試行可能 |
| [lw.plx](lw.plx) | 元動画と変換済みファイルの対応を照合・表示 | Perl。`-h` で元フォルダー、`-s` で保存先を指定 |
| [cropDetect.sh](cropDetect.sh) | 動画の複数箇所を調べてクロップ値を推定 | MPlayer。作業フォルダーに一時ファイルを作成・削除 |
| [renc.sh](renc.sh) | Avidemux CLI で動画を変換 | `/usr/local/bin/avidemux3_cli`。音声・映像コーデックと入力ファイルを指定 |
| [youtube_mux.sh](youtube_mux.sh) | 動画と音声をダウンロードして MP4 に結合 | `youtube-dl`、FFmpeg。結合成功後に中間ファイルを削除 |
| [avidemux3_cli_build.sh](avidemux3_cli_build.sh) | Avidemux のビルド・パッケージ作成を補助 | Avidemux ソースツリー、CMake、make など。旧バージョン向け |

### Transmission・Torrent

| ファイル | 用途 | 主な前提・動作 |
| --- | --- | --- |
| [clear_torrent_files.py](clear_torrent_files.py) | 対応する resume ファイルが見つからない `.torrent` などを削除 | `torrentool`、Unix の `syslog`。確認プロンプトなしで削除 |
| [TMctl.plx](TMctl.plx) | シーダー数・経過日数によるダウンロード開始、共有比率による登録削除 | Transmission RPC、`JSON::XS`、`LWP::UserAgent`、`Term::ExtendedColor`。接続先はコード内で設定 |
| [torrent_index_parser.py](torrent_index_parser.py) | HTML からリンクを抽出し、特定サイトのダウンロード処理を補助 | `requests`。他のコードから利用するパーサークラス群。単独実行用 CLI はなし |

### サーバー運用・ターミナル

| ファイル | 用途 | 主な前提・動作 |
| --- | --- | --- |
| [update-containers.sh](update-containers.sh) | Proxmox 上の稼働中 Alpine コンテナーを並列更新 | `pct`。対象 ID は `CTS=(100 103 104)`。各コンテナーで `apk update` と `apk upgrade` を実行 |
| [remake_cert.sh](remake_cert.sh) | CA・libvirt 用サーバー／クライアント証明書を再生成・配置 | GnuTLS の `certtool` と外部テンプレート。既存の鍵・証明書を削除・置換 |
| [ssdpd.sh](ssdpd.sh) | SSDP デーモンの起動・停止・状態確認 | Red Hat 系 SysV init の関数、`ssdpd`。インターフェースは `eth0` |
| [shout_reboot.sh](shout_reboot.sh) | shout を再起動し、httpd を再起動 | `shout`、`pgrep`、`service`。対象プロセスを強制終了 |
| [getNewRelease.sh](getNewRelease.sh) | Mastodon のリリースページを調べ、変更を通知 | `curl`、`whisper`。前回の値を `~/.mastodon` に保存。通知先は固定 |
| [dot.bashrc.sh](dot.bashrc.sh) | Bash のプロンプト・ロケール・履歴・エイリアス設定 | 個人環境用の `.bashrc` サンプル |
| [mem4screen.sh](mem4screen.sh) | メモリー使用率を表示 | Linux の `free`、`awk` |
| [256colors2.pl](256colors2.pl) | 端末の 256 色パレットを表示 | Perl、256 色対応端末 |

### Hubot・IRC

| ファイル | 用途 | 主な前提・動作 |
| --- | --- | --- |
| [hubot.sh](hubot.sh) | Hubot の起動・停止・再起動・状態確認 | Red Hat 系 SysV init、`/etc/sysconfig/hubot` の設定 |
| [irc.coffee](irc.coffee) | ISO-2022-JP と UTF-8 の変換を含む Hubot 用 IRC アダプター | Hubot、`irc`、`iconv`、`log`。接続設定は `HUBOT_IRC_*` 環境変数を参照 |
| [hubot-redmine-notifier.coffee](hubot-redmine-notifier.coffee) | Redmine のチケット作成・更新を Hubot に通知 | Redmine Webhook Plugin、Hubot、`log`。受信先は `/hubot/redmine-notify?room=<room>` |

### Windows・World of Tanks

| ファイル | 用途 | 主な前提・動作 |
| --- | --- | --- |
| [update_nick_font_size.py](update_nick_font_size.py) | XVM のプレイヤー名表示にフォントサイズ属性を追加 | `playersPanel.xc` を直接更新。Python 標準ライブラリのみ使用 |
| [rename_wotver.plx](rename_wotver.plx) | MOD 内のバージョンフォルダー名を変更 | Perl。`-v` でバージョン指定。MOD の保存先は固定 |
| [prep_resmod.bat](prep_resmod.bat) | MOD 用フォルダー・ジャンクション作成とアーカイブ展開 | Windows、7-Zip。ゲームのバージョンと各パスを要編集 |
| [prep_var.bat](prep_var.bat) | `temp`・`cache` フォルダーを作成 | Windows。作成先は `X:\var` |
| [Remove-KB.ps1](Remove-KB.ps1) | 指定した KB の更新プログラムをアンインストールする関数 | `Get-WmiObject`、`wusa.exe` を使用する Windows PowerShell 向けコード |

## 実行環境

必要なランタイムや依存ツールはスクリプトごとに異なります。

- **Python**: [pyproject.toml](pyproject.toml) は Python **3.14 以上**を指定し、`.python-version` も `3.14` です。`check_video.py` と `clear_torrent_files.py` は `syslog` を読み込むため、Unix 環境で利用します。
- **Bash / Perl**: 主に Linux 向けです。MediaInfo、MPlayer、Avidemux などは使うツールに応じて別途用意します。
- **Windows**: `.bat` はコマンドプロンプト、`Remove-KB.ps1` は Windows PowerShell を前提としています。
- **CoffeeScript**: 既存の Hubot 環境に組み込むコードです。このフォルダーには Node.js の依存関係を定義する `package.json` はありません。

Python の依存関係リストは現在 `dependencies = []` です。`torrentool` と `requests` は宣言されていないため、必要なスクリプトを使う環境に別途インストールしてください。

```console
python -m pip install torrentool requests
```

`pyproject.toml` には `tools = "tools:main"` というコマンド定義がありますが、ローカルの `src/tools/__init__.py` は挨拶を表示する雛形です。各ツールは以下のようにファイルを直接指定して実行します。

## 実行例

### XVM のフォントサイズを更新

`nickFormatLeft` / `nickFormatRight` のうち、対象のプレイヤー名を含む色付き `font` タグへ `size='{{xvm-stat?15|0}}'` を追加します。対象ファイルは上書きされるので、先にコピーを保存してください。

```console
python update_nick_font_size.py path/to/playersPanel.xc
```

パスを省略すると、カレントフォルダーの `playersPanel.xc` を処理します。

### 動画情報を登録・ファイル名を整理

Unix 環境で MediaInfo を用意し、次の外部テンプレートを配置してから実行します。

- コードが参照するパス: `/var/lib/misc/chech_video.template.txt`（`chech` はコード内の表記どおり）
- 想定出力: ファイル名・再生時間・コンテナー形式・高さ・映像形式・フレームレートの 6 項目を `/` で区切った文字列
- テンプレート本体はこのリポジトリには含まれていません。

```bash
python3 check_video.py --help
python3 check_video.py --home /path/to/videos --dbhome /path/to/database
```

通常実行では対象フォルダー直下を走査し、動画名・権限を変更して `movies.sqlite` に情報を記録します。パスには絶対パスを指定してください。

| オプション | 動作 |
| --- | --- |
| `--home` | 動画フォルダー。既定値は `/mnt/torrent/` |
| `--dbhome` | DB 保存先。既定値は `/var/lib/misc/` |
| `-f`, `--force` | DB に登録済みのファイルも再解析 |
| `-d`, `--delete` | 指定したファイル名のレコードを DB から削除 |
| `-r`, `--rescan` | 実ファイルが見つからないレコードを整理し、DB を VACUUM |

### 動画の移動・フォルダー削除を試行

```bash
perl sulvage_mp4.plx -t -h /path/to/videos
```

`-t` を付けると動画の移動とフォルダー削除を抑止し、予定操作を対象フォルダーの `sulvage_mp4.log` に書き出します。ログは試行時も上書きされます。実処理では元フォルダーを再帰削除するため、ログと残すファイルを確認してから `-t` を外してください。

### 端末表示を確認

```bash
perl 256colors2.pl
bash mem4screen.sh
```

## 利用前に確認する設定

- **削除・上書き**: 動画整理、Torrent 整理、証明書再生成、KB 削除は実データやシステムを変更します。共通の dry-run 機能はありません。
- **固定値**: `TMctl.plx` の RPC URL、`update-containers.sh` の `CTS`、WoT 関連のバージョン・保存先などは、コード内の値を利用環境に合わせて変更します。
- **外部ファイル**: MediaInfo のテンプレート、証明書テンプレート、Hubot の設定、MOD アーカイブなどは別途必要です。
- **旧環境への依存**: SysV init、古い Avidemux CLI、`youtube-dl`、サイト固有の HTML 解析などを含みます。現在の環境での互換性は個別に確認してください。

## リポジトリ構成

ルート直下に各スクリプトを配置しています。`pyproject.toml` と `uv.lock` は Python 環境用です。

[.gitignore](.gitignore) では `.venv/`、`.vscode/`、`__pycache__/` に加え、`src/` と `test/` も除外しています。そのため、ローカルにあるパッケージ雛形や実験用ファイルは、クローン先に含まれるとは限りません。
