import pandas as pd

from external_lib.deep_sort_pytorch.utils.parser import get_config
from external_lib.deep_sort_pytorch.deep_sort import DeepSort
from external_lib.NFLlib.score import NFLAssignmentScorer

from tqdm import tqdm
from lib.exelogger import print_info
import cv2



def deepsort_helmets(video_data,video_dir,deepsort_config,plot=False,pliot_frame=[]):

    myvideo = "Not found"

    assert not myvideo == "Not found";
    
    cfg = get_config();
    cfg.merge_from_dict(deepsort_config);


    deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT,
                        max_dist=cfg.DEEPSORT.MAX_DIST,
                        min_confidence=cfg.DEEPSORT.MIN_CONFIDENCE,
                        nms_max_overlap=cfg.DEEPSORT.NMS_MAX_OVERLAP,
                        max_iou_distance=cfg.DEEPSORT.MAX_IOU_DISTANCE,
                        max_age=cfg.DEEPSORT.MAX_AGE,
                        n_init=cfg.DEEPSORT.N_INIT,
                        nn_budget=cfg.DEEPSORT.NN_BUDGET,
                        use_cuda=True)

    video_data = video_data.sort_values("frame").reset_index(drop=True);

    ds = [];

    for frame,d in tqdm(video_data.groupby(),total=video_data["frame"].nunique()):
        
        ## ヘルメットの中心へ
        d['x'] = (d['left'] + round(d['width'] / 2))
        d['y'] = (d['top'] + round(d['height'] / 2))

        xywhs = d[["x","y","width","height"]].values


        ## 動画ファイルの読み込み
        cap = cv2.VideoCapture(f"{video_dir}/{myvideo}.mp4")
        
        ## シーケンスバー（映像ファイルの該当のフレームへ移動）
        cap.set(cv2.CAP_PROP_POS_FRAMES,frame-1);

        ## １フレーム分の読み込み
        success, image = cap.read();

        image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB);

        confs = np.ones([len(d),])
        clss = np.ones([len(d),])
        
        outputs = deepsort.update(xywhs, confs, clss, image)

       
        if (plot and frame > cfg.DEEPSORT.N_INIT) or (frame in plot_frames):
            for j, (output, conf) in enumerate(zip(outputs, confs)): 

                bboxes = output[0:4]
                id = output[4]
                cls = output[5]

                c = int(cls)  # integer class
                label = f'{id}'
                color = compute_color_for_id(id)
                im = plot_one_box(bboxes, image, label=label, color=color, line_thickness=2)
            fig, ax = plt.subplots(figsize=(15, 10))
            video_frame = d['video_frame'].values[0]
            ax.set_title(f'Deepsort labels: {video_frame}')
            plt.imshow(im)
            plt.show() 
    
        preds_df = pd.DataFrame(outputs, columns = ["left","top","right","bottom","deepsort_cluster","class"]);

        if (len(preds_df) > 0):
            d = pd.merge_asof(d.sort_values(['left','top']),
                              preds_df[['left','top','deepsort_cluster']] \
                              .sort_values(['left','top']), on='left', suffixes=('','_deepsort'),
                              direction='nearest')

        ds.append(d)
    dout = pd.concat(ds);
    return dout;


def add_deepsort_label_col(out):
    
    sortlabel_map = out.groupby("deepsort_cluster")["label"].value_counts()\
        .sort_values(ascending=False).to_frame() \
        .rename(columns={'label':'label_count'})\
        .reset_index() \
        .groupby(["deepsort_cluster"])\
        .first()["label"].to_dict()
    
    
    # Find the # of times that label appears for the deepsort_cluster.
    sortlabelcount_map = out.groupby('deepsort_cluster')['label'].value_counts() \
        .sort_values(ascending=False).to_frame() \
        .rename(columns={'label':'label_count'}) \
        .reset_index() \
        .groupby(['deepsort_cluster']) \
        .first()['label_count'].to_dict()

def score_vs_deepsort(myvideo, out, labels):

    # Score the base predictions compared to the deepsort postprocessed predictions.
    myvideo_mp4 = myvideo + '.mp4'
    labels_video = labels[labels["video"] == myvideo_mp4]
    scorer = NFLAssignmentScorer(labels_video)
    out_deduped = out.groupby(['video_frame','label']).first().reset_index()
    base_video_score = scorer.score(out_deduped)
    
    out_preds = out.drop('label', axis=1).rename(columns={'label_deepsort':'label'})
    print_info(out_preds.shape)
    out_preds = out_preds.groupby(['video_frame','label']).first().reset_index()
    print_info(out_preds.shape)
    deepsort_video_score = scorer.score(out_preds)
    print_info(f'{base_video_score:0.5f} before --> {deepsort_video_score:0.5f} deepsort')





















    









