setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        count: 0,
        mode: 1,  // 0 - one-by-one, 1 - multi
    },
    methods: {
        chooseMode(mode) {
            console.log('change from', this.mode, 'to', mode);
            this.mode = mode;
            window.localStorage.setItem("mode", mode);
            this.fetchPosts();
        },

        nextPosts() {
            window.scroll({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });
            let promises = this.posts.filter(p => !p.processed).map(p => {
                console.log(p.title);
                return this.updatePost(p, false);
            });

            Promise.all(promises).then((r) => {
                console.log('promises');
                console.log(r);
                this.fetchPosts();
            })
        },

        preload(posts) {
            posts.forEach(p => {
                if (p.media_type === 'photo') {
                    const img = new Image();
                    img.src = p.media_link;
                }
            });
        },

        fetchPosts() {
            let show = 5;
            let load = 5;
            if (this.mode === 0) {
                show = 1;
                load = 3;
            }
            this.$http.get(`/reddit/posts/?limit=${load}`)
                .then((response) => {
                    console.log(response.data);
                    this.count = response.data.count;
                    const posts = response.data.results.map(p => {
                        p.processed = false;
                        return p;
                    });
                    this.posts = posts.slice(0, show);
                    this.preload(posts.slice(show));
                    this.autoGrowTitleField();
                });
        },

        updatePost(post, accepted, title = null) {
            post.processed = true;
            return this.$http.put('/reddit/posts/' + post.id + '/',
                {
                    accepted: accepted,
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
                this.$refs['titleField'].forEach(target => {
                    target.style.height = "5px";
                    target.style.height = (target.scrollHeight + 38) + "px";
                });
            }, 100)
        }
    },
    mounted: function () {
        // todo: load mode from storage
        let mode = window.localStorage.getItem("mode");
        this.mode = mode === null ? 1 : parseInt(mode, 10);
        console.log(mode, this.mode);
        this.fetchPosts();
    }
});
