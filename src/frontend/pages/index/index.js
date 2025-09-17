const app = getApp();
const { request, processBody, addFavorite, removeFavorite, recordNewsView } = require('../../utils/api.js');

Page({
  data: {
    dataList: [],  // 存储第一个接口的数据
    titleList: [],  // 存储第二个接口的数据
    searchEntry: '',  // 搜索输入内容
    page: 1,  // 当前页码，从1开始，第一页数据
    pageSize: 15,  // 每次加载的条数
    isLoadingMore: false,  // 标识是否正在加载更多
    hasMoreData: true,  // 是否有更多数据
    showBackToTop: false,  // 是否显示置顶按钮
    loading: false, // 页面加载状态
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
      page: 1,  // 重置为第一页
      hasMoreData: true,  // 重置有更多数据标志
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
    
    // 使用 Promise.all 并行请求提高效率
    Promise.all([
      request('/tongzhigonggao'),
      request('/gettongzhititle')
    ]).then(([dataList, titleList]) => {
      that.setData({
        dataList: dataList,
        titleList: titleList,
        loading: false
      });
      if (callback) callback();
    }).catch(error => {
      console.error('Failed to fetch data:', error);
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

    // 显示加载提示
    wx.showToast({
        title: '加载中...',
        icon: 'loading',
        duration: 10000,  // 显示时间较长，以便加载完成后隐藏
        mask: true  // 遮罩
    });

    request(`/gettongzhimoredata?page=${page + 1}`)
      .then(newData => {
        if (newData.length < 15) {
          // 如果返回的数据条数少于每页条数，说明没有更多数据了
          that.setData({
            hasMoreData: false
          });
        }
        that.setData({
          dataList: dataList.concat(newData),  // 将新数据合并到已有数据中
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
    const news = index !== undefined ? this.data.dataList[index] : null;
    
    // 记录浏览
    if (news && news.id) {
      recordNewsView('tongzhigonggao', news.id, this.data.userInfo ? this.data.userInfo.id : null);
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
    
    // 这里需要根据实际情况调整，因为原始数据可能没有id字段
    // 暂时使用title作为标识
    const newsId = news.id || index;
    const newsTitle = news.title;
    
    // 添加收藏
    addFavorite(this.data.userInfo.id, 'tongzhigonggao', newsId, newsTitle)
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
      url: `/pages/show/show?entry=${entry}`,
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