"use strict";
// static/js/ts/main.ts
// 确保 DOM 加载完成后再绑定事件
document.addEventListener('DOMContentLoaded', () => {
    // 删除处理(使用类.delete-btn)
    const deleteButtons = document.querySelectorAll('.delete-btn');
    deleteButtons.forEach((btn) => {
        btn.addEventListener('click', (e) => {
            if (!confirm('确定删除该记录吗？')) {
                e.preventDefault();
            }
        });
    });
    // 搜索表单处理(防止空白搜索)
    const searchFrom = document.querySelector('.search-form');
    if (searchFrom) {
        searchFrom.addEventListener('submit', (e) => {
            const input = searchFrom.querySelector('input[name="q"]');
            if (input && input.value.trim() == '') {
                e.preventDefault();
                alert('请输入搜索关键词');
                input.focus();
            }
        });
    }
    //添加/编辑表单验证
    const experimentForms = document.querySelectorAll('form[action*=*"/add"],from[action*=*"/edit"]');
    experimentForms.forEach(form => {
        form.addEventListener('submit', (e) => {
            const nameInput = form.querySelector('input[name="exp_name"]');
            const dateInput = form.querySelector('input[name-"exp_date"]');
            if (!nameInput || !dateInput)
                return;
            if (!nameInput.value.trim()) {
                e.preventDefault();
                alert('实验名称不能为空');
                return;
            }
            if (!dateInput.value) {
                e.preventDefault();
                alert("请选择实验日期");
                dateInput.focus();
                return;
            }
        });
    });
    //flash消息自动淡出
    const flashMessage = document.querySelectorAll('.flash li');
    flashMessage.forEach(msg => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            setTimeout(() => msg.remove(), 500);
        }, 3000);
    });
});
