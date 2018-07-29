setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        count: 0,
    },
    methods: {
        preload(posts) {
            posts.forEach(p => {
                if (p.media_type === 'photo') {
                    const img = new Image();
                    img.src = p.media_link;
                }
            });
        },

        fetchPosts() {
            const show = 1;
            const load = 3;
            this.$http.get(`/reddit/posts/?limit=${load}`)
                .then((response) => {
                    console.log(response.data);
                    this.count = response.data.count;
                    const posts = response.data.results;
                    this.posts = posts.slice(0, show);
                    this.preload(posts.slice(show))
                });
        },
        updatePost(post, accepted, title = null) {
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
