// utils/api.js
const BASE_URL = 'https://founderbulusi.icu:1001';

// 统一的网络请求封装
const request = (url, method = 'GET', data = {}) => {
  return new Promise((resolve, reject) => {
    wx.request({
      url: BASE_URL + url,
      method: method,
      data: data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode === 200) {
          resolve(res.data);
        } else {
          reject(new Error(`请求失败，状态码：${res.statusCode}`));
        }
      },
      fail: (err) => {
        wx.showToast({
          title: '网络请求失败',
          icon: 'none'
        });
        reject(err);
      }
    });
  });
};

// 处理 body 参数的通用函数
const processBody = (bodyps) => {
  const result = {};

  for (const key in bodyps) {
    if (bodyps.hasOwnProperty(key)) {
      const value = bodyps[key];

      if (key.startsWith('p')) {
        result[key] = value;
      } else if (key.startsWith('img')) {
        result[key] = value;
      } else if (key.startsWith('div')) {
        result[key] = processBody(value);
      } else if (key.startsWith('ta')) {
        result[key] = value;
      }
    }
  }
  return result;
};

// 用户登录
const userLogin = (openid, userInfo) => {
  return request('/user/login', 'POST', {
    openid: openid,
    userInfo: userInfo
  });
};

// 添加收藏
const addFavorite = (userId, newsType, newsId, title) => {
  return request('/user/favorite', 'POST', {
    user_id: userId,
    news_type: newsType,
    news_id: newsId,
    title: title
  });
};

// 取消收藏
const removeFavorite = (userId, newsType, newsId) => {
  return request(`/user/favorite?user_id=${userId}&news_type=${newsType}&news_id=${newsId}`, 'DELETE');
};

// 获取用户收藏
const getUserFavorites = (userId) => {
  return request(`/user/favorites?user_id=${userId}`);
};

// 添加评论
const addComment = (userId, newsType, newsId, content, parentId = 0) => {
  return request('/news/comment', 'POST', {
    user_id: userId,
    news_type: newsType,
    news_id: newsId,
    content: content,
    parent_id: parentId
  });
};

// 获取新闻评论
const getNewsComments = (newsType, newsId) => {
  return request(`/news/comments?news_type=${newsType}&news_id=${newsId}`);
};

// 提交反馈
const submitFeedback = (content, contact = '', userId = null) => {
  const data = {
    content: content,
    contact: contact
  };
  if (userId) {
    data.user_id = userId;
  }
  return request('/feedback', 'POST', data);
};

// 记录新闻浏览
const recordNewsView = (newsType, newsId, userId = null) => {
  const data = {
    news_type: newsType,
    news_id: newsId
  };
  if (userId) {
    data.user_id = userId;
  }
  return request('/news/view', 'POST', data);
};

// 获取热门新闻
const getHotNews = (limit = 10) => {
  return request(`/news/hot?limit=${limit}`);
};

module.exports = {
  request,
  processBody,
  userLogin,
  addFavorite,
  removeFavorite,
  getUserFavorites,
  addComment,
  getNewsComments,
  submitFeedback,
  recordNewsView,
  getHotNews
};