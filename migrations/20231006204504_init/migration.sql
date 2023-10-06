-- CreateTable
CREATE TABLE "CharacterCard" (
    "id" SERIAL NOT NULL,
    "type" INTEGER NOT NULL,
    "oc_name" TEXT NOT NULL,
    "user_id" BIGINT NOT NULL,
    "talent" TEXT NOT NULL,
    "age" INTEGER NOT NULL,
    "weight" INTEGER NOT NULL,
    "height" INTEGER NOT NULL,
    "pronouns" TEXT NOT NULL,
    "likes" TEXT NOT NULL,
    "dislikes" TEXT NOT NULL,
    "fears" TEXT NOT NULL,
    "image_url" TEXT NOT NULL,

    CONSTRAINT "CharacterCard_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "CharacterCard_oc_name_key" ON "CharacterCard"("oc_name");
