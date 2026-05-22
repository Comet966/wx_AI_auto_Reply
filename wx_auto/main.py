"""WeChat Auto Reply Bot - Main Entry Point."""
import sys
import time
from pathlib import Path
from threading import Thread

from wx_auto.core.controller import controller
from wx_auto.core.detector import detector
from wx_auto.core.responder import responder
from wx_auto.core.screen import ocr_engine, screen_capture
from wx_auto.utils.config import config
from wx_auto.utils.logger import logger, setup_logger


class WeChatAutoBot:
    """Main WeChat Auto Reply Bot."""

    def __init__(self):
        """Initialize bot."""
        self._running = False
        self._thread = None

    def start(self) -> bool:
        """Start the bot.

        Returns:
            True if started successfully
        """
        logger.info("Starting WeChat Auto Reply Bot...")

        # Check API key
        if not config.api_key or config.api_key == "your-api-key-here":
            logger.error("请先在 config.yaml 中配置 API Key")
            return False

        # Ensure WeChat window is accessible
        if not controller.ensure_wechat():
            logger.error("无法找到微信窗口，请确保微信正在运行")
            return False

        # Note: User needs to manually specify message area region
        # This is a placeholder - you'll need to adjust based on your screen
        # Example: detector.set_region((100, 200, 400, 500))
        logger.warning("请设置消息检测区域: detector.set_region((left, top, width, height))")
        logger.warning("例如: detector.set_region((100, 300, 300, 400))")

        # Initialize detector
        if not detector.initialize():
            logger.error("无法初始化消息检测器")
            return False

        # Start main loop
        self._running = True
        self._thread = Thread(target=self._main_loop, daemon=True)
        self._thread.start()

        logger.info("Bot started successfully")
        return True

    def stop(self) -> None:
        """Stop the bot."""
        logger.info("Stopping bot...")
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Bot stopped")

    def _main_loop(self) -> None:
        """Main loop for checking and responding to messages."""
        while self._running:
            try:
                # Check for new messages
                if detector.detect_new_message():
                    logger.info("检测到新消息")

                    # Read message content (requires user to set region)
                    # messages = ocr_engine.recognize_text(screen_capture.capture(region))
                    # if messages:
                    #     reply_text = responder.generate_reply(messages)
                    #     responder.send_reply(reply_text)

                # Sleep for next check
                time.sleep(config.check_interval)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
                time.sleep(1)

    def run_interactive(self) -> None:
        """Run in interactive mode for testing."""
        logger.info("Running in interactive mode...")

        # Show instructions
        print("\n=== 微信自动回复助手 ===")
        print("1. 请手动打开微信并登录")
        print("2. 拖动聊天窗口到合适位置")
        print("3. 在下方输入消息区域坐标 (left, top, width, height)")
        print("   例��: 100,300,400,500")
        print("4. 按回车确认\n")

        region_input = input("请输入消息区域坐标 (留空使用默认值): ").strip()
        if region_input:
            try:
                left, top, width, height = map(int, region_input.split(","))
                detector.set_region((left, top, width, height))
                logger.info(f"检测区域设置为: ({left}, {top}, {width}, {height})")
            except ValueError:
                logger.error("格式错误，使用默认值")

        # Start
        self.start()

        # Wait for stop signal
        try:
            while self._running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()


def main():
    """Main entry point."""
    # Setup logging
    import argparse

    parser = argparse.ArgumentParser(description="微信自动回复助手")
    parser.add_argument("--debug", action="store_true", help="启用调试日志")
    parser.add_argument("-c", "--config", help="配置文件路径")
    args = parser.parse_args()

    # Configure logging
    if args.debug:
        import logging
        setup_logger(level=logging.DEBUG)

    # Load config if specified
    if args.config:
        from wx_auto.utils.config import Config

        config = Config(args.config)

    # Create and run bot
    bot = WeChatAutoBot()
    bot.run_interactive()


if __name__ == "__main__":
    main()