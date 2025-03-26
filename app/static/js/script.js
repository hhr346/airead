/**********************/
// 侧边栏收叠脚本
/**********************/
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const topbar = document.querySelector('.topbar');
    
    // 切换收叠状态
    sidebar.classList.toggle('collapsed');

    // 折叠后更改收叠图标和顶部栏的宽度和左侧距离
    if (sidebar.classList.contains('collapsed')) {
        toggleIcon.src = switchRight; // 收叠时显示右图标
        // topbar.style.left = '70px';
        // topbar.style.width = 'calc(100% - 70px - 200px)';
    } else {
        toggleIcon.src = switchLeft; // 展开时显示左图标
        // topbar.style.left = '250px';
        // topbar.style.width = 'calc(100% - 250px - 30px)';
    }
}

// 更新侧边栏
function updateSidebar() {
    fetch('/get_sidebar_data')
    .then(response => response.json())
    .then(data => {
        const rssFeeds = document.getElementById('rss-feeds');
        const currentUrl = window.location.pathname;  // 获取当前页面的URL
        rssFeeds.innerHTML = "";  // 清空现有的RSS feed区域

        // 遍历从后端获取的数据
        data.forEach(item => {
            const rssLink = document.createElement('a');  // 创建一个<a>标签
            rssLink.href = `/subscription/${item.id}`;    // 为每个RSS feed生成唯一链接
            rssLink.innerText = item.title;               // 显示RSS订阅源标题
            rssLink.classList.add('sidebar-item');        // 添加与固定选项一致的样式
            rssFeeds.appendChild(rssLink);                // 将新元素添加到rss-feeds区域

            // 如果当前URL匹配这个RSS订阅源的URL，则添加 'active' 类
            if (currentUrl === `/subscription/${item.id}`) {
                rssLink.classList.add('active');
            }
            
        });
    });
}



/**********************/
// 用户设置页面的脚本
/**********************/
document.addEventListener("DOMContentLoaded", function () {
    const editBtn = document.getElementById("edit-btn");
    const keywordInput = document.getElementById("keyword");

    // 点击编辑按钮，允许编辑关键词
    editBtn.addEventListener("click", function () {
        if (keywordInput.disabled) {
            // 启用输入框并切换按钮文本为"保存"
            keywordInput.disabled = false;
            keywordInput.focus();
            editBtn.innerHTML = "保存";
        } else {
            // 禁用输入框并切换按钮为编辑图标
            keywordInput.disabled = true;
            editBtn.innerHTML = "<img src='/static/images/edit.svg' alt='Edit'>";
            
            // 发送新的关键词到后端保存
            const newKeyword = keywordInput.value;
            fetch('/save_keyword', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ keyword: newKeyword }),
            })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);  // 后端返回的信息
            })
            .catch(error => {
                console.error('保存关键词时出错:', error);
            });
        }
    });

    // 登出按钮逻辑（可以根据需要重定向到登出页面）
    const logoutBtn = document.getElementById("logout-btn");
    logoutBtn.addEventListener("click", function () {
        alert("你已登出");
        // 在这里可以添加实际登出的逻辑
        window.location.href = "/logout";
    });
});



/**********************/
// 添加新的RSS feed
/**********************/
function importRSS() {
    var rssUrl = document.getElementById('rss-url').value;

    if (!rssUrl) {
        alert("请输入RSS链接");
        return;
    }
    // 使用Ajax异步请求提交RSS链接
    fetch('/import_rss', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'rss_url': rssUrl
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            alert(data.message);
            // 成功导入后，可以动态刷新侧边栏
            updateSidebar();
            // 同时清空输入框
            document.getElementById('rss-url').value = "";
        } else {
            alert(data.message);
        }
    });
}




/**********************/
/* 论文工具中的拖拽上传 */
/**********************/
document.getElementById('uploadImage').addEventListener('click', function () {
    document.getElementById('fileInput').click(); // 打开文件选择框
});

// 监听文件选择变化
document.getElementById('fileInput').addEventListener('change', function (event) {
    uploadFiles(event.target.files);
});

// 监听拖拽
const uploadBox = document.getElementById('uploadBox');
uploadBox.addEventListener('dragover', (event) => {
    event.preventDefault();
    uploadBox.classList.add('drag-over');
});

uploadBox.addEventListener('dragleave', () => {
    uploadBox.classList.remove('drag-over');
});

uploadBox.addEventListener('drop', (event) => {
    event.preventDefault();
    uploadBox.classList.remove('drag-over');
    const files = event.dataTransfer.files;
    uploadFiles(files); // 上传拖拽的文件
});

// 文件上传处理函数
function uploadFiles(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
        formData.append('file', files[i]); // 添加文件到FormData
    }

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload_file', true);

    // 上传进度条更新
    xhr.upload.onprogress = function (event) {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            document.getElementById('progressBar').style.width = percentComplete + '%';
        }
    };

    // 上传完成的处理
    xhr.onload = function () {
        if (xhr.status === 200) {
            document.getElementById('uploadStatus').innerText = '上传成功!';
            document.getElementById('fileName').innerText = files[0].name;
        } else {
            document.getElementById('uploadStatus').innerText = '上传失败!';
        }
    };

    xhr.send(formData);
}


/**********************/
/* 论文工具中的发送消息 */
/**********************/
function sendMessage() {
    const userInput = document.getElementById('user-input-text').value;
    
    if (userInput) {
        fetch('/ask-question', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ question: userInput })
        })
        .then(response => response.json())
        .then(data => {
            // Append AI answer and user input to the chat
            const chatBox = document.getElementById('chat-box');
            const userMessage = '<div class="user-message"><p>' + userInput + '</p></div>';
            const aiMessage = '<div class="ai-message"><p>' + data.answer + '</p></div>';
            chatBox.innerHTML += userMessage + aiMessage;
            document.getElementById('user-input-text').value = ''; // Clear input field
        })
        .catch(error => console.error('Error:', error));
    }

}

