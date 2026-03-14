import sys
import json
import os
import qrcode
import hashlib
import uuid
import platform
import subprocess
from pathlib import Path


def get_machine_id():
    """
    获取机器唯一标识的替代方法
    """
    system = platform.system()

    try:
        if system == "Windows":
            # Windows系统：获取Windows机器GUID
            import winreg
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                                 "SOFTWARE\\Microsoft\\Cryptography")
            machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
            winreg.CloseKey(key)
            machine_id = machine_guid

        elif system == "Darwin":  # macOS
            # macOS系统：获取IOPlatformUUID
            result = subprocess.run(
                ["ioreg", "-rd1", "-c", "IOPlatformExpertDevice"],
                capture_output=True,
                text=True
            )
            for line in result.stdout.split('\n'):
                if "IOPlatformUUID" in line:
                    machine_id = line.split('"')[-2]
                    break
            else:
                machine_id = str(uuid.getnode())  # 备用方案

        elif system == "Linux":
            # Linux系统：尝试多种方法
            possible_paths = [
                "/etc/machine-id",
                "/var/lib/dbus/machine-id",
                "/sys/class/dmi/id/product_uuid"
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, 'r') as f:
                        machine_id = f.read().strip()
                    break
            else:
                # 如果都没有，使用MAC地址
                machine_id = str(uuid.getnode())
        else:
            # 其他系统使用MAC地址
            machine_id = str(uuid.getnode())

    except Exception as e:
        print(f"获取机器ID时出错: {e}，使用备用方案")
        # 最后的备用方案：使用主机名+MAC地址组合
        hostname = platform.node()
        mac = str(uuid.getnode())
        machine_id = hashlib.sha256(f"{hostname}{mac}".encode()).hexdigest()

    # 生成一个稳定的哈希ID（类似原machineid.hashed_id的功能）
    hashed_id = hashlib.sha256(f"jd_payment_skill_{machine_id}".encode()).hexdigest()

    return hashed_id[:16]  # 返回前16位作为简化版本


def get_user_token():
    """
    从上级目录的configs/config.json获取userToken
    如果文件或目录不存在，则生成链接和二维码
    """
    # 获取当前文件所在目录的上级目录中的configs文件夹
    current_dir = Path(__file__).parent.absolute()
    parent_dir = current_dir.parent
    config_dir = parent_dir / 'configs'
    config_file = config_dir / 'config.json'

    # 检查配置文件是否存在
    if config_dir.exists() and config_file.exists():
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
                if 'userToken' in config_data:
                    print(f"从配置文件读取到userToken: {config_data['userToken']}")
                    return config_data['userToken']
                else:
                    print("配置文件中不存在userToken字段")
        except Exception as e:
            print(f"读取配置文件失败: {e}")

    # 配置文件不存在或没有userToken，生成链接和二维码
    print("未找到userToken配置，正在生成授权链接和二维码...")

    # 创建tmp目录（如果不存在）
    tmp_dir = current_dir / 'tmp'
    tmp_dir.mkdir(exist_ok=True)

    # 生成唯一的token（使用UUID作为示例）
    generated_token = str(uuid.uuid4())

    # 生成授权链接
    auth_url = f"https://example.com/auth?token={generated_token}"

    # 生成二维码
    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5
    )
    qr.add_data(auth_url)
    qr.make(fit=True)

    # 创建二维码图片
    qr_image = qr.make_image(fill_color="black", back_color="white")

    # 保存二维码图片
    qr_filename = f"auth_qr_{generated_token[:8]}.png"
    qr_path = tmp_dir / qr_filename
    qr_image.save(qr_path)

    print(f"已生成授权链接: {auth_url}")
    print(f"二维码已保存至: {qr_path}")
    return None


def deal_payment(merchant_wallet_address: str, amount: int, payer_authorization_sign: str):
    # 使用自定义的get_machine_id函数替代machineid.hashed_id
    machine_id = get_machine_id()

    # 获取user_token
    user_token = get_user_token()
    if user_token is None:
        return None

    test_token = "AABBCCDD"
    print(f"处理支付中... 商家: {merchant_wallet_address}, 金额: {amount}, 付款签名: {payer_authorization_sign}")
    print(f"机器ID: {machine_id}")
    print(f"用户令牌: {user_token}")
    return test_token


if __name__ == "__main__":
    # 检查传入参数的数量是否正确 (1个脚本名 + 3个参数 = 4)
    if len(sys.argv) != 4:
        print("用法: python main.py <merchant_wallet> <amount> <payer_wallet>")
        sys.exit(1)

    # 获取参数
    merchant = sys.argv[1]
    # 注意：命令行传入的参数默认都是字符串，所以 amount 需要转换成 int
    try:
        amount = int(sys.argv[2])
    except ValueError:
        print("错误: 金额必须是整数")
        sys.exit(1)

    payer = sys.argv[3]

    # 传入函数并执行
    token = deal_payment(merchant, amount, payer)

    if token is None:
        print("支付未成功")
    else:
        print(f"支付凭证: {token}")