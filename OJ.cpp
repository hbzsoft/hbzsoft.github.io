//The program requires three parameters.Usage:
//./OJ user_program input_file answer
//Example:
//./OJ a.cpp a.in a.out
//Notice:
//You may need to use data redirection to save the result.
#include <iostream>
#include <fstream>
#include <cstdlib>

using namespace std;
int main(int argc,char *argv[])
{
	string program_path=argv[1];
	
	string compile_cmd="g++ -o check_program "+program_path;
	system(&compile_cmd[0]);
	ifstream check_ce("check_program");
	if(!check_ce)
	{
		cout<<"Compile Error"<<endl;
		return 0;
	}
	ofstream output("user.ans");
	output.close();
	string check_cmd="./check_program >user.ans <";
	check_cmd+=argv[2];
	system(&check_cmd[0]);
	ofstream user_md5("usermd5");
	user_md5.close();
	system("md5sum user.ans >usermd5");
	ofstream answer_md5("answermd5");
	answer_md5.close();
	string verification="md5sum ";
	verification+=argv[3];
	verification+=" >answermd5";
	system(&verification[0]);
	ifstream user_get("usermd5");
	string usermd5;
	user_get>>usermd5;
	ifstream ans_get("answermd5");
	string ansmd5;
	ans_get>>ansmd5;
	if(usermd5==ansmd5)
	{
		cout<<"Accepted"<<endl;
	}
	else
	{
		cout<<"Wrong Answer"<<endl;
	}
	system("rm check_program");
	system("rm answermd5");
	system("rm user.ans");
	system("rm usermd5");
	return 0;
}
