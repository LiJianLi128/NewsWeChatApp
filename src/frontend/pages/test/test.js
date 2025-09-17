Page({
  data: {
    bodyResult: {},
    order: [],
    fabutime: '',
    laiyuan: '',
    title: '',
    loading: false
  },
  
  onLoad: function (options) {
    const eventChannel = this.getOpenerEventChannel();
    eventChannel.on('acceptData', function (data) {
      this.setData({
        bodyResult: data.bodyResult,
        order: data.order,
        fabutime: data.fabutime,
        laiyuan: data.laiyuan,
        title: data.title
      });
    }.bind(this));
  },
  
  onPullDownRefresh() {
    // 重新加载数据
    wx.stopPullDownRefresh();
    wx.showToast({
      title: '已刷新',
      icon: 'success'
    });
  },
  
  // 图片加载失败处理
  onImageError: function(e) {
    console.log('图片加载失败', e);
    wx.showToast({
      title: '图片加载失败',
      icon: 'none'
    });
  },
  
  // 图片点击预览
  onImageTap: function(e) {
    const src = e.currentTarget.dataset.src;
    if (src) {
      wx.previewImage({
        urls: [src]
      });
    }
  }
});