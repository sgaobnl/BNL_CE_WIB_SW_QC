import GUI.send_email as send_email
sender = "bnlr216@gmail.com"
password = "vvef tosp minf wwhf"
receiver = "lke@bnl.gov"

def send_cold_down_email():
    send_email.send_email(
        sender, password, receiver,
        f"CTS has been cold down [{pre_info['test_site']}]",
        '"** Please Double confirm: reach level3, heat LED off"'
    )