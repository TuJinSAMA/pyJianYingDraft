import pyJianYingDraft as draft

def export():
    # 此前需要将剪映打开，并位于目录页
    ctrl = draft.Jianying_controller()

    # 然后即可导出指定名称的草稿
    ctrl.export_draft("test_draft", r"E:\SoftwareCache\Jianyingprerender")



if __name__ == '__main__':
    export()