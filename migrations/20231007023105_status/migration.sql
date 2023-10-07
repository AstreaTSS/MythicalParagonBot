-- CreateEnum
CREATE TYPE "Status" AS ENUM ('ALIVE', 'DEAD', 'MISSING');

-- AlterTable
ALTER TABLE "CharacterCard" ADD COLUMN     "status" "Status" NOT NULL DEFAULT 'ALIVE';
