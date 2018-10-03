setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        postsCount: '...',
    },
    methods: {
        fetchPosts() {
            this.postsCount = '...';
            this.$http.get(`/reddit/posts/?limit=20`)
                .then((response) => {
                    console.log(response.data);
                    this.postsCount = response.data.count;
                    let posts = response.data.results.map(p => {
                        p.processed = false;
                        return p;
                    });
                    this.posts = this.posts.concat(posts);
                    this.autoGrowTitleField();
                });
        },

        nextPosts() {
            window.scroll({
                top: 0,
                left: 0,
            });
            this.postsCount = '...';
            let posts = this.posts;
            this.posts = [];
            let rejectedPosts = posts
                .filter(p => !p.processed)
                .map(p => {
                    p.processed = true;
                    return p.id;
                });
            console.log(rejectedPosts);

            this.$http.post('/reddit/posts/reject/', {
                posts: rejectedPosts,
            }).then(() => {
                return this.fetchPosts();
            });
        },

        updatePost(post, title = null) {
            post.processed = true;
            return this.$http.put('/reddit/posts/' + post.id + '/',
                {
                    title: title,
                })
                .then((response) => {
                    console.log(response.data);
                    if (this.mode === 0) {
                        this.fetchPosts();
                    }
                    return response.data;
                });
        },

        autoGrowTitleField() {
            setTimeout(() => {
                if (!this.$refs['titleField']) {
                    return;
                }
                this.$refs['titleField'].forEach(target => {
                    target.style.height = "5px";
                    target.style.height = (target.scrollHeight + 38) + "px";
                });
            }, 100)
        }
    },
    mounted: function () {
        this.fetchPosts();
    }
});
