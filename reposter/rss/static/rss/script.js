function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = jQuery.trim(cookies[i]);
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

let csrftoken = getCookie('csrftoken');

Vue.http.interceptors.push(function (request) {
    // modify headers
    request.headers.set('X-CSRFToken', csrftoken);
});

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        channels: [],
        actionsResult: '',
        cleanDays: 1,
        action: false,
    },
    methods: {
        fetchChannels(searchTerm = "") {
            this.$http.get('/api/channels/', {params: {search: searchTerm}})
                .then((response) => {
                    console.log(response.data);
                    this.channels = response.data;
                });
        },
        publishPosts() {
            this.action = true;
            this.$http.post('/api/publish/')
                .then((response) => {
                    this.action = false;
                    this.actionsResult = response.data;
                });
        },
        refreshChannels() {
            this.action = true;
            this.$http.post('/api/refresh/')
                .then((response) => {
                    this.action = false;
                    this.actionsResult = response.data;
                });
        },
        cleanOldPosts() {
            this.action = true;
            this.$http.post('/api/clean/', {days: this.cleanDays})
                .then((response) => {
                        this.action = false;
                        this.actionsResult = response.data;
                    },
                    (error) => {
                        this.action = false;
                        this.actionsResult = error.data;
                    }
                );
        },
    },
    mounted: function () {
        this.fetchChannels();
    }
});

const searchInput = document.getElementById('search-input');
let timeout = null;
searchInput.onkeyup = function () {
    clearTimeout(timeout);
    timeout = setTimeout(function () {
        app.fetchChannels(searchInput.value);
    }, 500);
};