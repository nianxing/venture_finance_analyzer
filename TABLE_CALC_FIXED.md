# 表格计算逻辑修复说明

## 🔧 修复内容

已经重新设计了表格计算逻辑，现在表格之间互相连接的公式完全正确。

## ✨ 核心改进

### 1. 新增 `recalculateAllRows()` 函数
从第一行开始，逐行重新计算所有数据，确保：
- ✅ 每行的投前估值正确继承上一行的投后估值
- ✅ 创始人持股按正确的累积稀释公式计算
- ✅ 股权比例自动计算
- ✅ 数据完全一致

### 2. 计算逻辑

#### 投前估值继承
```javascript
if (preMoney === 0 && i > 0 && previousPostMoney > 0) {
    preMoney = previousPostMoney;
    inputs[1].value = preMoney;
}
```

#### 投前/投后/投资额关系
```javascript
// 投后估值 = 投前估值 + 投资额
if (preMoney > 0 && investment > 0) {
    postMoney = preMoney + investment;
}

// 投资额 = 投后估值 - 投前估值
else if (preMoney > 0 && postMoney > 0) {
    investment = postMoney - preMoney;
}

// 投前估值 = 投后估值 - 投资额
else if (investment > 0 && postMoney > 0) {
    preMoney = postMoney - investment;
}
```

#### 创始人持股累积稀释
```javascript
// 第一行
previousFounderPct = 100;

// 每一行
const dilutionFactor = (100 - investorPct) / 100;
const founderPct = previousFounderPct * dilutionFactor;

// 更新为下一行的基础
previousFounderPct = founderPct;
```

## 📊 数据流

1. 用户修改任意单元格
2. 先根据修改字段进行初步计算
3. 调用 `recalculateAllRows()` 从第一行开始重新计算
4. 确保所有数据一致

## 🎯 使用示例

### 示例1：从模板开始
1. 选择"完整融资（A+B+C轮）"模板
2. 可以看到：
   - A轮：投前2000，投资800，投后2800，新投资者28.57%，创始人71.43%
   - B轮：投前2800，投资2000，投后4800，新投资者41.67%，创始人41.67%
   - C轮：投前4800，投资5000，投后9800，新投资者51.02%，创始人20.41%

### 示例2：修改数据
1. 修改A轮的投资额从800改为1000
2. 自动更新：
   - A轮投后：2000 → 3000
   - A轮新投资者股权%：自动更新
   - A轮创始人持股%：自动更新
   - B轮投前：自动更新为3000
   - B轮后续所有计算自动更新

### 示例3：添加新行
1. 点击"+ 添加轮次"
2. 新行的投前自动继承上一行的投后
3. 新行的创始人持股自动继承上一行的持股比例

## 🔍 验证方法

启动服务器并测试：

```bash
python start_web.py
```

然后访问 http://localhost:5000 测试：

1. **选择模板** - 验证数据正确
2. **修改任意单元格** - 验证实时更新
3. **添加新行** - 验证继承正确
4. **切换计算模式** - 验证锁定/解锁正确

## ✅ 修复的问题

### 修复前：
- ❌ 创始人持股没有正确累积稀释
- ❌ 跨行数据不一致
- ❌ 投前估值继承有问题

### 修复后：
- ✅ 创始人持股正确累积：100% → 71.43% → 41.67% → 20.41%
- ✅ 投前估值自动继承：上一行的投后 = 下一行的投前
- ✅ 所有数据实时同步更新
- ✅ 完全一致的数据流


