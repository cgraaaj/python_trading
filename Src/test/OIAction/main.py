from OIAction import OIAction
from teleBot import Tele


def main():
    stock = "TATAMOTORS"
    oi_action = OIAction(stock)
    option_chain_data = oi_action.analyze_stock()
    oi_action.generate_xsls()
    oi_action.generate_df_to_img()
    oi_action.generate_oi_strike_png()
    oi_action.generate_change_in_oi_strike_png()
    tele = Tele(
        chat_ids_fname="test_ids",
        data_path=f"/home/pudge/Trading/python_trading/Src/test/OIAction/data/{stock}",
    )
    tele.send()


if __name__ == "__main__":
    main()
