setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        postsCount: '...',
        initialized: false,
    },
    methods: {
        fetchPosts() {
            this.postsCount = '...';
            this.$http.get(`/reddit/posts/?limit=20`)
                .then((response) => {
                    this.initialized = true;
                    this.postsCount = response.data.count;
                    this.posts = response.data.results.map(p => {
                        p.processed = false;
                        return p;
                    });
                    this.autoGrowTitleField();
                });
        },

        nextPosts() {
            this.initialized = false;
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

            this.$http.post('/reddit/posts/reject/', {
                posts: rejectedPosts,
            }).then(() => {
                return this.fetchPosts();
            });
        },

        updatePost(post, title = null) {
            post.processed = true;
            return this.$http.put('/reddit/posts/' + post.id + '/', {
                title: title,
            }).then((response) => {
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
        },

        autoPlayVideo() {
            let postsElements = document.querySelectorAll('.post');
            postsElements.forEach(p => {
                let video = p.querySelector('video');
                if (!video) {
                    return;
                }
                if (window.scrollY > p.offsetTop - p.clientHeight && window.scrollY < p.offsetTop) {
                    video.play();
                } else {
                    video.pause();
                }
            })
        }
    },
    mounted: function () {
        this.fetchPosts();

        let update = null;
        this.autoPlayVideo();
        window.addEventListener('scroll', function () {
            // auto video play
            clearTimeout(update);
            update = setTimeout(() => {
                this.autoPlayVideo();
            }, 200)
        })
    }
});
