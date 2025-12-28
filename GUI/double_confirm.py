import time


def double_confirm(prompt_yes_no,
                   confirm_yes_msg,
                   confirm_no_msg,
                   sleep_seconds=None,
                   yes_action=None,
                   no_action=None):
    """
    A generic double-confirm function.

    prompt_yes_no:     the initial "y/n" question
    confirm_yes_msg:   message shown when user chose 'y'
    confirm_no_msg:    message shown when user chose 'n'
    sleep_seconds:     seconds to sleep if user confirms 'y' (optional)
    yes_action:        function executed after sleep (optional)
    no_action:         function executed when user skips (optional)
    """

    while True:
        choice = input(prompt_yes_no).lower()

        if choice == 'y':
            print(confirm_yes_msg)
            com = input('>> ')
            if com == "confirm":
                if sleep_seconds:
                    time.sleep(sleep_seconds)
                if yes_action:
                    yes_action()
                break
            else:
                print("Retry Please")

        elif choice == 'n':
            print(confirm_no_msg)
            com = input('>> ')
            if com == "confirm":
                if no_action:
                    no_action()
                break
            else:
                print("Retry Please")

        else:
            print("Please type y or n.")
