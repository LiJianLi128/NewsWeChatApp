const app = getApp();
const { request, processBody, addFavorite, removeFavorite, recordNewsView } = require('../../utils/api.js');

Page({
  data: {
    dataList: [],  // 存储第一个接口的数据
    titleList: [],  // 存储第二个接口的数据
    searchEntry: '',  // 搜索输入内容
    page: 1,  // 当前页码
    pageSize: 15,  // 每次加载的条数
    isLoadingMore: false,  // 标识是否正在加载更多
    hasMoreData: true,  // 是否有更多数据
    loading: false, // 页面加载状态
    showBackToTop: false,  // 是否显示置顶按钮
    userInfo: null,
    hasUserInfo: false
  },

  onLoad: function () {
    // 获取用户信息
    const userInfo = wx.getStorageSync('userInfo');
    if (userInfo) {
      this.setData({
        userInfo: userInfo,
        hasUserInfo: true
      });
    }
    
    this.loadData();  // 初次加载页面数据
  },

  // 下拉刷新事件处理
  onPullDownRefresh: function () {
    // 重置数据
    this.setData({
      page: 1,
      hasMoreData: true,
      dataList: [],  // 清空当前数据
      titleList: []  // 清空轮播图数据
    });
    this.loadData(() => {
      wx.stopPullDownRefresh();  // 停止下拉刷新动画
      wx.showToast({
        title: '刷新成功',
        icon: 'success',
        duration: 2000
      });
    });
  },

  // 上拉触底事件处理
  onReachBottom: function () {
    if (this.data.hasMoreData && !this.data.isLoadingMore) {
      this.loadMoreData();
    }
  },

  // 加载数据
  loadData: function (callback) {
    var that = this;
    this.setData({ loading: true });
    
    request('/xiaoyuandongtai')
      .then(res => {
        that.setData({
          dataList: res,
          titleList: res.slice(0, 4),  // 只获取前四条数据
          loading: false
        });
        if (callback) callback();
      })
      .catch(error => {
        console.error('Failed to fetch dataList:', error);
        that.setData({ loading: false });
        wx.showToast({
          title: '数据加载失败',
          icon: 'none'
        });
        if (callback) callback();
      });
  },

  // 加载更多数据（上拉加载）
  loadMoreData: function () {
    var that = this;
    const { page, dataList } = this.data;

    this.setData({ isLoadingMore: true });  // 标记正在加载更多

    wx.showToast({
        title: '加载中...',
        icon: 'loading',
        duration: 10000,
        mask: true
    });

    request(`/getyaowenmoredata?page=${page + 1}`)
      .then(newData => {
        if (newData.length < 15) {
          that.setData({
            hasMoreData: false  // 没有更多数据
          });
        }
        that.setData({
          dataList: dataList.concat(newData),  // 合并新数据
          page: page + 1  // 页码增加
        });
      })
      .catch(error => {
        console.error('Failed to load more data:', error);
        wx.showToast({
          title: '加载失败',
          icon: 'none'
        });
      })
      .finally(() => {
        that.setData({ isLoadingMore: false });  // 取消加载标志
        wx.hideToast();  // 隐藏加载提示
      });
  },

  // 监听轮播图的切换事件
  swiperChange(e) {
    this.setData({
      currentSwiperIndex: e.detail.current
    });
  },

  // url请求数据
  onCardTap: function (e) {
    const url = e.currentTarget.dataset.url;
    const index = e.currentTarget.dataset.index;
    const news = this.data.dataList[index];
    
    // 记录浏览
    if (news && news.id) {
      recordNewsView('xiaoyuandongtai', news.id, this.data.userInfo ? this.data.userInfo.id : null);
    }
    
    wx.showLoading({
      title: '加载中...',
    });
    
    request(`/geturldata?url=${url}`)
      .then(res => {
        if (res && res.length > 0) {
          this.processData(res);
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
    const bodyResult = processBody(body);

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

  // 收藏/取消收藏
  toggleFavorite: function (e) {
    if (!this.data.hasUserInfo) {
      wx.showToast({
        title: '请先登录',
        icon: 'none'
      });
      return;
    }
    
    const index = e.currentTarget.dataset.index;
    const news = this.data.dataList[index];
    
    // 添加收藏
    addFavorite(this.data.userInfo.id, 'xiaoyuandongtai', news.id || index, news.title)
      .then(res => {
        wx.showToast({
          title: '收藏成功',
          icon: 'success'
        });
      })
      .catch(err => {
        console.error('收藏失败', err);
        wx.showToast({
          title: '收藏失败',
          icon: 'none'
        });
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

    if (!entry) {
      wx.showToast({
        title: '请输入搜索内容',
        icon: 'none'
      });
      return;
    }

    wx.navigateTo({
      url: `/pages/show2/show2?entry=${entry}`,
    });
  },
  
  // 监听页面滚动
  onPageScroll: function (e) {
    const scrollTop = e.scrollTop;  // 获取页面的滚动高度
    if (scrollTop > 300) {  // 当页面滚动超过300px时，显示按钮
      this.setData({
        showBackToTop: true
      });
    } else {
      this.setData({
        showBackToTop: false
      });
    }
  },

  // 置顶功能
  scrollToTop: function () {
    wx.pageScrollTo({
      scrollTop: 0,  // 滚动到顶部
      duration: 300  // 动画持续时间，单位为毫秒
    });
  },
});