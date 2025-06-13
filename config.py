from dotenv import load_dotenv
import os
import sys
from logger import logging
from language import get_translation


class Config:
    def __init__(self):
        # 获取应用程序的根目录路径
        if getattr(sys, "frozen", False):
            # 如果是打包后的可执行文件
            application_path = os.path.dirname(sys.executable)
        else:
            # 如果是开发环境
            application_path = os.path.dirname(os.path.abspath(__file__))

        # 指定 .env 文件的路径
        dotenv_path = os.path.join(application_path, ".env")

        if not os.path.exists(dotenv_path):
            raise FileNotFoundError(get_translation("file_not_exists", path=dotenv_path))

        # 加载 .env 文件
        load_dotenv(dotenv_path)

        self.imap = False
        self.temp_mail = self._clean_env_value(os.getenv("TEMP_MAIL", "")).split("@")[0]
        self.temp_mail_epin = self._clean_env_value(os.getenv("TEMP_MAIL_EPIN", ""))
        self.temp_mail_ext = self._clean_env_value(os.getenv("TEMP_MAIL_EXT", ""))
        self.domain = self._clean_env_value(os.getenv("DOMAIN", ""))

        # 如果临时邮箱为null则加载IMAP
        if self.temp_mail == "null":
            self.imap = True
            self.imap_server = self._clean_env_value(os.getenv("IMAP_SERVER", ""))
            self.imap_port = self._clean_env_value(os.getenv("IMAP_PORT", ""))
            self.imap_user = self._clean_env_value(os.getenv("IMAP_USER", ""))
            self.imap_pass = self._clean_env_value(os.getenv("IMAP_PASS", ""))
            self.imap_dir = self._clean_env_value(os.getenv("IMAP_DIR", "inbox"))

        self.check_config()

    def _clean_env_value(self, value):
        """清理环境变量值，移除引号和注释

        Args:
            value: 原始环境变量值

        Returns:
            str: 清理后的值
        """
        if not value:
            return ""

        # 移除首尾空白
        value = value.strip()

        # 移除引号
        value = value.strip("'\"")

        # 移除注释（以 # 开头的部分）
        if '#' in value:
            value = value.split('#')[0].strip()

        return value

    def get_temp_mail(self):

        return self.temp_mail

    def get_temp_mail_epin(self):

        return self.temp_mail_epin

    def get_temp_mail_ext(self):

        return self.temp_mail_ext

    def get_imap(self):
        if not self.imap:
            return False
        return {
            "imap_server": self.imap_server,
            "imap_port": self.imap_port,
            "imap_user": self.imap_user,
            "imap_pass": self.imap_pass,
            "imap_dir": self.imap_dir,
        }

    def get_domain(self):
        return self.domain

    def get_protocol(self):
        """获取邮件协议类型

        Returns:
            str: 'IMAP' 或 'POP3'
        """
        return self._clean_env_value(os.getenv('IMAP_PROTOCOL', 'POP3'))

    def check_config(self):
        """检查配置项是否有效

        检查规则：
        1. 如果使用 tempmail.plus，需要配置 TEMP_MAIL 和 DOMAIN
        2. 如果使用 IMAP，需要配置 IMAP_SERVER、IMAP_PORT、IMAP_USER、IMAP_PASS
        3. IMAP_DIR 是可选的
        """
        # 基础配置检查
        required_configs = {
            "domain": "domain_not_configured",
        }

        # 检查基础配置
        for key, error_key in required_configs.items():
            if not self.check_is_valid(getattr(self, key)):
                raise ValueError(get_translation(error_key))

        # 检查邮箱配置
        if self.temp_mail != "null":
            # tempmail.plus 模式
            if not self.check_is_valid(self.temp_mail):
                raise ValueError(get_translation("temp_mail_not_configured"))
        else:
            # IMAP 模式
            imap_configs = {
                "imap_server": "imap_server_not_configured",
                "imap_port": "imap_port_not_configured",
                "imap_user": "imap_user_not_configured",
                "imap_pass": "imap_pass_not_configured",
            }

            for key, error_key in imap_configs.items():
                value = getattr(self, key)
                if value == "null" or not self.check_is_valid(value):
                    raise ValueError(get_translation(error_key))

            # IMAP_DIR 是可选的，如果设置了就检查其有效性
            if self.imap_dir != "null" and not self.check_is_valid(self.imap_dir):
                raise ValueError(get_translation("imap_dir_invalid"))

    def check_is_valid(self, value):
        """检查配置项是否有效

        Args:
            value: 配置项的值

        Returns:
            bool: 配置项是否有效
        """
        return isinstance(value, str) and len(str(value).strip()) > 0

    def print_config(self):
        if self.imap:
            logging.info(get_translation("imap_server", server=self.imap_server))
            logging.info(get_translation("imap_port", port=self.imap_port))
            logging.info(get_translation("imap_username", username=self.imap_user))
            logging.info(get_translation("imap_password", password='*' * len(self.imap_pass)))
            logging.info(get_translation("imap_inbox_dir", dir=self.imap_dir))
        if self.temp_mail != "null":
            logging.info(get_translation("temp_mail", mail=f"{self.temp_mail}{self.temp_mail_ext}"))
        logging.info(get_translation("domain", domain=self.domain))


# 使用示例
if __name__ == "__main__":
    try:
        config = Config()
        print(get_translation("env_variables_loaded"))
        config.print_config()
    except ValueError as e:
        print(get_translation("error_prefix", error=e))
