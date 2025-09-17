const { request } = require('../../utils/api.js');

Page({
  data: {
    content: '',
    contact: '',
    userInfo: null,
    hasUserInfo: false,
    submitting: false
  },

  onLoad: function () {
    // 获取用户信息
    const app = getApp();
    if (app.globalData.userInfo) {
      this.setData({
        userInfo: app.globalData.userInfo,
        hasUserInfo: true
      });
    } else {
      // 从本地存储获取
      const userInfo = wx.getStorageSync('userInfo');
      if (userInfo) {
        this.setData({
          userInfo: userInfo,
          hasUserInfo: true
        });
      }
    }
  },

  // 输入内容变化
  onContentInput: function (e) {
    this.setData({
      content: e.detail.value
    });
  },

  // 联系方式变化
  onContactInput: function (e) {
    this.setData({
      contact: e.detail.value
    });
  },

  // 提交反馈
  submitFeedback: function () {
    if (!this.data.content.trim()) {
      wx.showToast({
        title: '请输入反馈内容',
        icon: 'none'
      });
      return;
    }

    this.setData({ submitting: true });

    const data = {
      content: this.data.content,
      contact: this.data.contact
    };

    // 如果用户已登录，添加用户ID
    if (this.data.hasUserInfo) {
      data.user_id = this.data.userInfo.id;
    }

    request('/feedback', 'POST', data)
      .then(res => {
        wx.showToast({
          title: '提交成功',
          icon: 'success'
        });
        // 清空输入
        this.setData({
          content: '',
          contact: '',
          submitting: false
        });
      })
      .catch(err => {
        console.error('提交反馈失败', err);
        wx.showToast({
          title: '提交失败',
          icon: 'none'
        });
        this.setData({ submitting: false });
      });
  },

  // 下拉刷新
  onPullDownRefresh: function () {
    wx.stopPullDownRefresh();
  }
});