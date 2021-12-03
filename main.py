import curses

def main():
    screen = curses.initscr()
    screen.refresh()


    screen.addstr(0, 0, 'Some text at (0, 0)')
    screen.addstr(10, 10, 'Some text at (10, 10)')

    screen.addch(5, 5, 'X')

    screen.refresh()



    curses.napms(2000)
    curses.endwin()


if __name__ == '__main__':
    main()
