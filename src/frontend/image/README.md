# 图片资源说明

## 需要添加的图片资源

为了使小程序功能完整，需要添加以下图片资源到 `image` 文件夹：

### 1. TabBar图标（建议尺寸：81px × 81px）
- `index.png` - 通知公告未选中图标
- `indexhl.png` - 通知公告选中图标
- `new.png` - 校园动态未选中图标
- `newhl.png` - 校园动态选中图标
- `hot.png` - 热门新闻未选中图标
- `hot_selected.png` - 热门新闻选中图标
- `我的.png` - 我的未选中图标
- `我的l.png` - 我的选中图标

### 2. 功能图标
- `up-arrow.png` - 置顶按钮图标
- `empty.png` - 空状态显示图标
- `favorite.png` - 未收藏状态图标
- `favorite_selected.png` - 已收藏状态图标

## 图标设计建议

### 尺寸要求
- TabBar图标：81px × 81px
- 功能图标：根据实际显示需求设计（建议60px × 60px以内）

### 颜色规范
- 未选中状态：建议使用灰色系 (#999999)
- 选中状态：建议使用主色调 (#00b26a)
- 功能图标：建议使用主色调或与页面风格协调的颜色

### 格式要求
- 建议使用PNG格式以保证透明度效果
- 注意图片压缩以减小包体积
- 保持图标风格统一

## 图标使用说明

### TabBar图标路径配置
在 `app.json` 中已配置以下图标路径：
```json
{
  "tabBar": {
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "通知公告",
        "iconPath": "image/index.png",
        "selectedIconPath": "image/indexhl.png"
      },
      {
        "pagePath": "pages/list/list",
        "text": "校园动态",
        "iconPath": "image/new.png",
        "selectedIconPath": "image/newhl.png"
      },
      {
        "pagePath": "pages/hot/hot",
        "text": "热门新闻",
        "iconPath": "image/hot.png",
        "selectedIconPath": "image/hot_selected.png"
      },
      {
        "pagePath": "pages/logs/logs",
        "text": "我的",
        "iconPath": "image/我的.png",
        "selectedIconPath": "image/我的l.png"
      }
    ]
  }
}
```

### 功能图标使用
- 置顶按钮图标在首页和列表页使用
- 空状态图标在收藏页和热门新闻页使用
- 收藏图标在新闻列表页使用

## 注意事项

1. 所有图标应保持风格一致
2. 注意图标的可用性和识别度
3. 建议提供不同分辨率的图标以适配不同设备
4. 定期检查图标链接是否正确