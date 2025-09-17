const { request } = require('../../utils/api.js');

Page({
  data: {
    hotNews: [],
    loading: false
  },

  onLoad: function () {
    this.loadHotNews();
  },

  // 加载热门新闻
  loadHotNews: function (callback) {
    this.setData({ loading: true });
    
    request('/news/hot?limit=20')
      .then(res => {
        this.setData({
          hotNews: res.hot_news || [],
          loading: false
        });
        if (callback) callback();
      })
      .catch(err => {
        console.error('加载热门新闻失败', err);
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        });
        this.setData({ loading: false });
        if (callback) callback();
      });
  },

  // 跳转到新闻详情
  goToNewsDetail: function (e) {
    const index = e.currentTarget.dataset.index;
    const news = this.data.hotNews[index];
    
    // 根据新闻类型跳转到不同页面
    if (news.type === 'tongzhigonggao') {
      // 对于通知公告，我们需要获取详细信息
      wx.navigateTo({
        url: `/pages/show/show?url=${news.url}&title=${encodeURIComponent(news.title)}`
      });
    } else if (news.type === 'xiaoyuandongtai') {
      wx.navigateTo({
        url: `/pages/show2/show2?url=${news.url}&title=${encodeURIComponent(news.title)}`
      });
    }
  },

  // 下拉刷新
  onPullDownRefresh: function () {
    this.loadHotNews(() => {
      wx.stopPullDownRefresh();
      wx.showToast({
        title: '刷新成功',
        icon: 'success'
      });
    });
  }
});