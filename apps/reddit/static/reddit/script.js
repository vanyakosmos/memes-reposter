setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        postsCount: '...',
        initialized: false,
        keep: 20,
        limit: 5,
        offset: 3,
        finished: false,
    },
    methods: {
        fetchPosts() {
            this.initialized = false;
            return this.$http.get(`/reddit/posts/?limit=${this.limit}`)
                .then((response) => {
                    this.initialized = true;
                    this.postsCount = response.data.count;
                    let posts = response.data.results.map(p => {
                        p.processed = false;
                        return p;
                    });
                    if (posts.length !== 0) {
                        // remove already present
                        let ids = this.posts.map(p => p.id);
                        for (let p of posts) {
                            if (ids.indexOf(p.id) === -1) {
                                this.posts.push(p);
                            }
                        }
                        // leave only top `keep` newest
                        // this.posts = this.posts.slice(-this.keep);
                    }
                    this.finished = this.postsCount === posts.length || posts.length === 0;
                    this.autoGrowTitleField();
                });
        },

        async rejectPosts(posts) {
            let rejectedPosts = posts
                .filter(p => !p.processed)
                .map(p => {
                    p.processed = true;
                    return p.id;
                });
            if (rejectedPosts.length === 0) {
                return;
            }
            return this.$http.post('/reddit/posts/reject/', {
                posts: rejectedPosts,
            })
        },

        finish() {
            this.rejectPosts(this.posts)
                .then(() => {
                    this.posts = [];
                    return this.fetchPosts();
                })
        },

        rejectOldAndFetchNewPosts() {
            if (this.finished) {
                return;
            }
            let firstPosts = this.posts.slice(0, this.posts.length - this.offset);

            return this.rejectPosts(firstPosts)
                .then(() => {
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
            let postsElements = document.querySelectorAll('.post:not(.processed)');
            postsElements.forEach(p => {
                let video = p.querySelector('video');
                if (!video) {
                    return;
                }
                let bot = p.offsetTop + video.offsetTop;
                let mid = window.scrollY + window.innerHeight / 2;
                let top = bot + video.clientHeight;

                if (mid > bot && mid < top) {
                    video.play();
                } else {
                    video.pause();
                }
            });
        },

        autoLoadNewPosts() {
            let cards = document.querySelectorAll('div.post');
            let lastCard = cards[cards.length - 1];
            if (lastCard && this.initialized && lastCard.offsetTop - 500 < window.scrollY) {
                this.rejectOldAndFetchNewPosts();
            }
        }

    },
    mounted: function () {
        this.fetchPosts()
            .then(() => {
                this.autoPlayVideo();
            });

        let update = null;
        window.addEventListener('scroll', () => {
            clearTimeout(update);
            update = setTimeout(() => {
                // play video in screen
                this.autoPlayVideo();
                // load new posts
                this.autoLoadNewPosts();
            }, 200)
        })
    }
});
