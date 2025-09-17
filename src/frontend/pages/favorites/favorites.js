const { request } = require('../../utils/api.js');

Page({
  data: {
    favorites: [],
    loading: false,
    userInfo: null,
    hasUserInfo: false
  },

  onLoad: function () {
    // 获取用户信息
    const app = getApp();
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      });
      this.loadFavorites();
    } else {
      // 从本地存储获取
      const userInfo = wx.getStorageSync('userInfo');
      if (userInfo) {
        this.setData({
          userInfo: userInfo,
          hasUserInfo: true
        });
        this.loadFavorites();
      }
    }
  },

  onShow: function () {
    // 每次显示页面时重新加载收藏列表
    if (this.data.hasUserInfo) {
      this.loadFavorites();
    }
  },

  // 加载收藏列表
  loadFavorites: function () {
    if (!this.data.hasUserInfo) return;
    
    this.setData({ loading: true });
    
    request(`/user/favorites?user_id=${this.data.userInfo.id}`)
      .then(res => {
        this.setData({
          favorites: res.favorites || [],
          loading: false
        });
      })
      .catch(err => {
        console.error('加载收藏列表失败', err);
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        });
        this.setData({ loading: false });
      });
  },

  // 取消收藏
  removeFavorite: function (e) {
    const index = e.currentTarget.dataset.index;
    const favorite = this.data.favorites[index];
    
    wx.showModal({
      title: '提示',
      content: '确定要取消收藏吗？',
      success: (res) => {
        if (res.confirm) {
          request(`/user/favorite?user_id=${this.data.userInfo.id}&news_type=${favorite.news_type}&news_id=${favorite.news_id}`, 'DELETE')
            .then(res => {
              wx.showToast({
                title: '取消成功',
                icon: 'success'
              });
              // 重新加载收藏列表
              this.loadFavorites();
            })
            .catch(err => {
              console.error('取消收藏失败', err);
              wx.showToast({
                title: '取消失败',
                icon: 'none'
              });
            });
        }
      }
    });
  },

  // 跳转到新闻详情
  goToNewsDetail: function (e) {
    const index = e.currentTarget.dataset.index;
    const favorite = this.data.favorites[index];
    
    // 根据新闻类型跳转到不同页面
    if (favorite.news_type === 'tongzhigonggao') {
      wx.navigateTo({
        url: `/pages/show/show?url=${favorite.news_id}&title=${encodeURIComponent(favorite.title)}`
      });
    } else if (favorite.news_type === 'xiaoyuandongtai') {
      wx.navigateTo({
        url: `/pages/show2/show2?url=${favorite.news_id}&title=${encodeURIComponent(favorite.title)}`
      });
    }
  },

  // 下拉刷新
  onPullDownRefresh: function () {
    this.loadFavorites(() => {
      wx.stopPullDownRefresh();
    });
  }
});