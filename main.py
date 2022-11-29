import keep_alive


def main():
    while True:
        try:
            keep_alive.listening()
        except:
            main()


if __name__ == '__main__':
    main()
