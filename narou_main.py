import argparse as ap
import datetime
import narou_func as tm

default_json_file = "../tempdata/temp.json"

def year4_type(s: str) -> int:
    """'yyyy' 形式の年をチェックする type 関数"""
    try:
        if len(s) != 4:
            raise ValueError("年は4桁で指定してください。")
        # datetime.strptime を使って、数字であり、かつ有効な年の範囲か検証
        datetime.datetime.strptime(s, '%Y')
        return int(s)
    except ValueError:
        # argparseはArgumentTypeErrorで適切なエラーメッセージを表示
        raise ap.ArgumentTypeError(f"'{s}' は 'yyyy' 形式の有効な年ではありません。")

if __name__ == "__main__":
    parser = ap.ArgumentParser(
        prog="なろうAPIツール",
        description="なろうAPIでDB取得、統計出力するツール")
    parser.add_argument('-lm', nargs=3, help='指定された開始年～終了年のタイトル長の平均を出力します。LIMIT_COUNTでTOP N件を指定します。 -lm [start year] [end year] [limit count]', metavar=('START_YEAR', 'END_YEAR', 'LIMIT_COUNT'))
    parser.add_argument('-lh', nargs=2, help='指定された年のタイトル長のヒストグラムを出力します。LIMIT_COUNTでTOP N件を指定します。-lh [year] [limit count]', metavar=('YEAR', 'LIMIT_COUNT'))
    parser.add_argument('-nt', nargs=2, help='指定された開始年～終了年の連載／短編の数を出力します。-nt [start year] [end year]', type=year4_type, metavar=('START_YEAR', 'END_YEAR'))
    args=parser.parse_args()

    if args.lm:
        try:
            start_year = year4_type(args.lm[0])
            end_year = year4_type(args.lm[1])
            limit_count = int(args.lm[2])
            if limit_count < 1:
                raise ValueError
        except ValueError:
            parser.error(f"LIMIT_COUNT には1以上の整数を指定してください: '{args.lm[2]}'")
        except ap.ArgumentTypeError as e:
            parser.error(str(e))
        tm.get_title_length_mean(start_year, end_year, limit_count)
    
    if args.lh:
        try:
            year = year4_type(args.lh[0])
            limit_count = int(args.lh[1])
            if limit_count < 1:
                raise ValueError
        except ValueError:
            parser.error(f"LIMIT_COUNT には1以上の整数を指定してください: '{args.lh[1]}'")
        except ap.ArgumentTypeError as e:
            parser.error(str(e))
        tm.get_title_length_hist(year, limit_count)
    
    if args.nt:
        start_year = args.nt[0]
        end_year = args.nt[1]
        tm.get_nobel_type_nums(start_year, end_year)
