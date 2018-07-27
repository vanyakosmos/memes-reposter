setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        count: 0,
    },
    methods: {
        fetchPosts() {
            this.$http.get('/reddit/posts/?limit=1')
                .then((response) => {
                    console.log(response.data);
                    this.count = response.data.count;
                    this.posts = response.data.results;
                });
        },
        updatePost(post, accepted, title=null) {
            console.log(post.title, accepted);
            this.$http.put('/reddit/posts/' + post.id + '/',
                {
                    accepted: accepted,
                    title: title,
                })
                .then((response) => {
                    console.log(response.data);
                    this.fetchPosts()
                });
        },
    },
    mounted: function () {
        this.fetchPosts();
    }
});
