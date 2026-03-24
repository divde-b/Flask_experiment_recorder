/**
 * NetLab 笔记前端交互脚本
 * 负责:
 *  -删除记录前的确认弹窗
 *  -搜索框空白提交拦截
 *  -一俺家/编辑表单的必填项认证
 *  -Flash消息自动淡出
 */
// 等待 DOM 树完全加载完后在执行，避免找不到元素
document.addEventListener('DOMContentLoaded', () => {

        // ======================== 1.确认删除 ============================ //
    const deleteButtons = document.querySelectorAll('.delete-btn');
    // 选择所有带 .delete-bth 类的按钮（删除按钮）
    deleteButtons.forEach((btn) => {
        //弹出确认框，如果用户取消，则阻止表单提交
        btn.addEventListener('click', (e) => {
            if (!confirm('确定删除该记录吗？')) {
                e.preventDefault();
            }
        });
    });

        // ======================== 2.搜索表单验证 ============================ //
        // 选择class="seach-from"的表单
    const searchFrom = document.querySelector<HTMLFormElement>('.search-form');
    if (searchFrom) {
        searchFrom.addEventListener('submit', (e) => {
            // 找到搜索关键词输入框
            const input = searchFrom.querySelector<HTMLInputElement>('input[name="q"]');
            // 如果输入框为空且内容为空或只有空格
            if (input && input.value.trim() == '') {
                e.preventDefault();     // 阻止提交
                alert('请输入搜索关键词')       //提示用户
                input.focus();      // 让输入框获得焦点
            }
        });
    }

        // ======================== 3.添加/编辑表单验证 ============================ //
        // 选择 action 包含 "/add" 或 "/edit" 的表单
    const experimentForms = document.querySelectorAll<HTMLFormElement>('form[action*=*"/add"],from[action*=*"/edit"]');
    experimentForms.forEach(form => {
        form.addEventListener('submit',(e) => {
            // 获取实验名称输入框和日期输入框
            const nameInput = form.querySelector<HTMLInputElement>('input[name="exp_name"]');
            const dateInput = form.querySelector<HTMLInputElement>('input[name-"exp_date"]');
            // 如果找不到关键字字段，跳过验证
            if (!nameInput || !dateInput) return;
            //验证是否为空
            if (!nameInput.value.trim()) {
                e.preventDefault();
                alert('实验名称不能为空');
                return;
            }
            //验证日期是否已选择
            if (!dateInput.value) {
                e.preventDefault();
                alert("请选择实验日期");
                dateInput.focus();
                return;
            }
        });
    });

        // ========================4.Flash消息自动弹出 ============================ //
        // 选择所有 flash 消息列表项
    const flashMessage = document.querySelectorAll<HTMLLIElement>('.flash li');
    flashMessage.forEach( msg => {
        // 设置定时器，3秒后开始淡出
        setTimeout(() => {
            msg.style.transition = 'opacity 0.5s';
            msg.style.opacity = '0';
            // 淡出完成后移除元素。避免页面元素残留
            setTimeout(() => msg.remove(),500);},3000);
        });

    });
