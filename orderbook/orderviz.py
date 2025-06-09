import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# 模拟交易参数
price_levels = np.round(np.arange(99.5, 100.6, 0.1), 2)
frames = 40
order_book = {price: {'bid': [], 'ask': []} for price in price_levels}
position_record = []

# 初始化挂单（每个挂单有id、量、时间戳）
order_id_counter = 1
np.random.seed(0)

def create_order(side, frame):
    global order_id_counter
    price = np.random.choice(price_levels)
    volume = np.random.randint(1, 5)
    order = {'id': order_id_counter, 'volume': volume, 'time': frame}
    order_id_counter += 1
    if side == 'bid':
        order_book[price]['bid'].append(order)
    else:
        order_book[price]['ask'].append(order)

# 初始化前几帧挂单
for f in range(5):
    for _ in range(5):
        create_order(np.random.choice(['bid', 'ask']), f)

# 创建挂单和成交序列
event_log = []
for f in range(frames):
    action = np.random.choice(['new_order', 'trade', 'cancel'])
    if action == 'new_order':
        side = np.random.choice(['bid', 'ask'])
        create_order(side, f)
    elif action == 'trade':
        # 模拟一次撮合（简单模拟：中间价位成交）
        price = round(100.0 + np.random.choice([-0.1, 0, 0.1]), 2)
        trade_volume = np.random.randint(1, 4)

        bids = order_book[price]['bid']
        asks = order_book[price]['ask']

        if bids and asks:
            bid_order = bids[0]
            ask_order = asks[0]
            matched_volume = min(bid_order['volume'], ask_order['volume'], trade_volume)

            bid_order['volume'] -= matched_volume
            ask_order['volume'] -= matched_volume

            if bid_order['volume'] <= 0:
                bids.pop(0)
            if ask_order['volume'] <= 0:
                asks.pop(0)

            event_log.append((f, price, matched_volume))
            position_record.append((f, matched_volume))  # 简单记录成买方持仓增加

    elif action == 'cancel':
        price = np.random.choice(price_levels)
        side = np.random.choice(['bid', 'ask'])
        orders = order_book[price][side]
        if orders:
            orders.pop(0)

# 动画绘图
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 8), gridspec_kw={'height_ratios': [3, 1]})
bars_bid = {}
bars_ask = {}

def update(frame):
    ax1.clear()
    ax2.clear()

    ax1.set_title(f"Order Book Depth - Frame {frame}")
    ax1.set_xlim(0, 5)
    ax1.set_ylim(price_levels[0] - 0.1, price_levels[-1] + 0.1)

    for i, price in enumerate(price_levels):
        # 从下往上画 bid
        x_offset = 0
        for order in order_book[price]['bid']:
            ax1.barh(price, order['volume'], left=x_offset, height=0.08, color='green')
            x_offset += order['volume']

        # 从上往下画 ask
        x_offset = 0
        for order in order_book[price]['ask']:
            ax1.barh(price, -order['volume'], left=x_offset, height=0.08, color='red')
            x_offset += order['volume']

    ax1.axhline(100, color='black', linestyle='--', linewidth=0.5)

    # 绘制简单持仓演变图
    pos = [v for t, v in position_record if t <= frame]
    ax2.plot(range(len(pos)), np.cumsum(pos), color='blue')
    ax2.set_title("Cumulative Position (Buy Side)")
    ax2.set_xlim(0, frames)
    ax2.set_ylim(0, max(1, np.sum([v for _, v in position_record])) + 1)


ani = FuncAnimation(fig, update, frames=frames, interval=400)
plt.show()  # 让动画展示出来

