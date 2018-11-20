<div class="scroll c-tAll">
<?php
if(isset($models))
    foreach($models as $comment) : ?>
<?php // if comment.state == 1 OR (user is defined AND user.group_id > 3) ?>

<div class="comment comment_id="<?=$comment->id ?>">
    <div class="c-avatar" rel="<?php echo $comment->author ? $comment->author->id : "";?>" style="background-image: url(<?php echo $comment->author ? $comment->getAuthorPhoto() : "";?>)"></div>
    <div class="comment-info row">
        <div class="col-md-9">
            <div class="row c-user"><?=$comment->getLogin() ?></div>
            <div class="row c-txt"><?=$comment->txt ?></div>
            <?php /* if($comment->state == 0): ?>
            <div class="c-not-approved">
                <a class="noajax" href="/comments/default/view?id=<?=$comment->id ?>">Moderate</a>
            </div>
            <?php endif; */ ?>

            <div class="row c-attach">
                <?php foreach($comment->getAttach() as $attach): ?>
                    <?php if($attach->typeImages()): ?>
                    <a class="fancybox ajax" rel="gallery_id-<?=$comment->id ?>" href="<?=$attach->getUrl() ?>" onclick="fancyBox(this);return false;">
                        <div class="col-md-4">
                            <img src="<?=$attach->getThumbUrl() ?>">
                        </div>
                    </a>
                    <?php elseif($attach->typeDocuments()): ?>
                    <a class="noajax" href="<?=$attach->getUrl() ?>">
                        <div class="col-md-1">
                            <img src="/template/front/img/filetypes-icons/text-file-icon.png" width=64/>
                        </div>
                    </a>
                    <?php endif; ?>
                <?php endforeach; ?>
            </div>
        </div>

        <div class="col-lg-3">
            <div class="c-date"><?=$comment->getDate() ?></div>

        </div>
        <!-- <div class="c-like"><span>{{ comment.likes }}</span></div> -->
    </div>
    <div class="c-responce">
        <?php if($comment->children): ?>
        <div class="answers">
            <?php echo $this->render('_index_item', ['models' => $comment->children, 'options' => $options]); ?>
        </div>
        <?php endif; ?>
    </div>
    <div style="clear:both;"></div>
</div>
<?php endforeach; ?>
</div>