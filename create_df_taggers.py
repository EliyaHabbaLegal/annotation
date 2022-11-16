
# create df of the taggers and their status for each sentence
import os

from manage_txt import TxtDirManager


TAGGERS_NAMES = ["tagger1", "tagger2", "tagger3"]

# create main section
if __name__ == "__main__":

    idm = TxtDirManager("txt_dir")
    df  = idm.get_df()
    #create new df for each tagger with 100 random sentences
    for tagger in TAGGERS_NAMES:
        df_tagger = df.sample(100)
        df_tagger["tagger"] = tagger
        df_tagger["status"] = "not annotated"
        if not os.path.exists(f"{tagger}.csv"):
            os.makedirs("taggers", exist_ok=True)
            df_tagger.to_csv(os.path.join("taggers", f"{tagger}.csv"), index=False)