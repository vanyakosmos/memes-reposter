setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
    },
    methods: {
        fetchPosts() {
            this.$http.get('/reddit/posts/?limit=5')
                .then((response) => {
                    console.log(response.data);
                    this.posts = response.data.results;
                });
        },
        updatePost(post, accepted) {
            console.log(post.title, accepted);
            this.$http.put('/reddit/posts/' + post.id + '/',
                {accepted: accepted})
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
