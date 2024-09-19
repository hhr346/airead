// 侧边栏收叠脚本
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const toggleIcon = document.getElementById('toggle-icon');
    
    // 切换收叠状态
    sidebar.classList.toggle('collapsed');
    
    // 切换图标
    if (sidebar.classList.contains('collapsed')) {
        toggleIcon.src = switchRight; // 收叠时显示右图标
    } else {
        toggleIcon.src = switchLeft; // 展开时显示左图标
    }
}



// 论文工具相关的脚本
// 获取按钮和文本框的DOM元素
document.getElementById('generate-summary').addEventListener('click', function() {
    // 显示AI对话的文本框
    document.getElementById('conversation-box').style.display = 'block';
});

document.getElementById('generate-ppt').addEventListener('click', function() {
    // 这里可以触发后端逻辑生成PPT，并把下载链接放到文本框里
    document.getElementById('ppt-download-link').value = 'PPT下载链接生成成功！';
});



// 以下是用户设置页面的脚本
document.addEventListener("DOMContentLoaded", function () {
    const editBtn = document.getElementById("edit-btn");
    const keywordInput = document.getElementById("keyword");

    // 点击编辑按钮，允许编辑关键词
    editBtn.addEventListener("click", function () {
        if (keywordInput.disabled) {
            keywordInput.disabled = false;
            keywordInput.focus();
            editBtn.innerHTML = "保存";
        } else {
            keywordInput.disabled = true;
            editBtn.innerHTML = "<img src='/static/images/edit.png' alt='Edit'>";
            // 你可以在这里添加保存逻辑，例如发送数据到后端
            console.log("关键词已更新为: " + keywordInput.value);
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





// 添加新的RSS feed
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

function updateSidebar() {
    fetch('/get_sidebar_data')
    .then(response => response.json())
    .then(data => {
        const rssFeeds = document.getElementById('rss-feeds');
        const currentUrl = window.location.pathname;  // 获取当前页面的URL
        // rssFeeds.innerHTML = "";  // 清空现有的RSS feed区域，或许不应该清空？只在更新时清空？为什么这个清空似乎去掉了之后也不会累加呢？

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
