from telegram_bot import startup
import asyncio


def main():
	loop = asyncio.new_event_loop()
	loop.run_until_complete(startup())


if __name__ == '__main__':
	main()


