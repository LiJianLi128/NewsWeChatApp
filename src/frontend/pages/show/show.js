const { request, processBody } = require('../../utils/api.js');

Page({
  data: {
    entry: '',
    dataList: [],
    searchEntry: '',  // 搜索输入内容
    loading: false
  },
  
  onLoad: function (options) {
    // 接收从上一个页面传递过来的 entry 参数
    this.setData({
      entry: options.entry
    });

    // 发起网络请求，使用传递过来的 entry 参数
    this.fetchData(options.entry);
  },
  
  fetchData: function (entry) {
    this.setData({ loading: true });
    
    // 发起网络请求，传递 table 和 entry 参数
    request(`/ddatabase?table=tongzhigonggao&entry=${entry}`)
      .then(res => {
        if (res && res.length > 0) {
          // 更新页面数据
          this.setData({
            dataList: res,
            loading: false
          });
        } else {
          wx.showToast({
            title: '没有匹配的结果',
            icon: 'none'
          });
          this.setData({ loading: false });
        }
      })
      .catch(err => {
        console.error('搜索请求失败', err);
        wx.showToast({
          title: '搜索失败，请稍后再试',
          icon: 'none'
        });
        this.setData({ loading: false });
      });
  },
  
  // 监听搜索输入框
  onSearchInput: function (e) {
    this.setData({
      searchEntry: e.detail.value
    });
  },

  // 处理搜索按钮点击事件
  onSearch: function () {
    const entry = this.data.searchEntry;

    // 检查是否有输入内容
    if (!entry) {
      wx.showToast({
        title: '请输入搜索内容',
        icon: 'none'
      });
      return;
    }
    // 跳转到新页面并传递搜索参数
    wx.navigateTo({
      url: `/pages/show/show?entry=${entry}`,
    });
  },

  // url请求数据
  onCardTap: function (e) {
    const url = e.currentTarget.dataset.url;
    
    wx.showLoading({
      title: '加载中...',
    });
    
    // 发起请求，获取数据
    request(`/geturldata?url=${url}`)
      .then(res => {
        if (res && res.length > 0) {
          this.processData(res);  // 处理返回的数据并渲染新页面
        }
      })
      .catch(err => {
        console.error('请求失败', err);
        wx.showToast({
          title: '数据加载失败',
          icon: 'none'
        });
      })
      .finally(() => {
        wx.hideLoading();
      });
  },
  
  // 处理数据并渲染新页面
  processData: function (data) {
    const { fabutime, laiyuan, title, order, body } = data[0];

    // 处理 body 字典
    const bodyResult = processBody(body);

    // 跳转到新页面并传递处理后的数据
    wx.navigateTo({
      url: '/pages/test/test',
      success: (res) => {
        res.eventChannel.emit('acceptData', { bodyResult, fabutime, laiyuan, title, order });
      },
      fail: (err) => {
        console.error('Navigation failed: ', err);
        wx.showToast({
          title: '页面跳转失败',
          icon: 'none'
        });
      }
    });
  },
  
  onPullDownRefresh() {
    // 重新加载数据
    this.fetchData(this.data.entry);
    wx.stopPullDownRefresh();
  },
});