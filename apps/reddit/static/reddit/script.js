setupCSRF();

const app = new Vue({
    delimiters: ['[[', ']]'],
    el: '#app',
    data: {
        posts: [],
        capacity: '...',
        length: 10,
    },
    methods: {
        lengthChanged(e) {
            let num = e.target.valueAsNumber;
            if (num >= 0 && num <= 20) {
                this.length = num;
                window.localStorage.setItem("length", num);
            }
        },

        nextPosts() {
            window.scroll({
                top: 0,
                left: 0,
            });
            this.capacity = '...';
            let posts = this.posts;
            this.posts = [];
            let promises = posts.filter(p => !p.processed).map(p => {
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
            let show = this.length;
            let load = this.length;
            if (this.length === 0) {
                show = 1;
                load = 3;
            }
            this.capacity = '...';
            this.$http.get(`/reddit/posts/?limit=${load}`)
                .then((response) => {
                    console.log(response.data);
                    this.capacity = response.data.count;
                    const posts = response.data.results.map(p => {
                        p.processed = false;
                        return p;
                    });
                    this.posts = posts.slice(0, show);
                    if (this.length === 0) {
                        this.preload(posts.slice(show));
                    }
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
        let length = window.localStorage.getItem("length");
        this.length = length === null ? 10 : parseInt(length, 10);
        console.log('start', length, this.length);
        this.fetchPosts();
    }
});
